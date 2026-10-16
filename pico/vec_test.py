# vec_test.py
# MyChip_FP_MAC MPW 칩 - 전체 테스트 벡터(vectors.bin) 재생 + 판정 (Raspberry Pi Pico 2 W / MicroPython)
#
#  보드 구성은 smoke_test.py 와 동일
#   피코 -> 74HCT245(5V) -> 74HC14(슈미트, 반전) -> 칩 입력 5개 (i_clk, i_rstn, i_ssn, i_sclk, i_mosi)
#   피코 <- 74LVC245A(3.3V) <---------------------- 칩 출력 2개 (o_miso, o_cmd_done)
#
#  동작
#   - 벡터 1개 = i_clk 1사이클. PIO 가 i_clk 을 직접 만들고, 같은 PIO 가 입력 4개를 i_clk 에 맞춰 내보낸다.
#       (i_clk 하강 직후 입력 인가 -> 상승 -> 다음 하강 직전 MISO/done 샘플)  = sim/tb_vec.v 와 같은 타이밍
#   - DMA 2개: 벡터 -> PIO TX FIFO,  PIO RX FIFO -> 측정 버퍼.  CPU 는 끼어들지 않으므로 사이클 정확.
#   - 측정값을 vectors.bin 의 mask/기대값 비트와 비교해 bin 별 PASS/FAIL.
#   - 칩은 전부 정적 논리라, 청크 사이에서 i_clk 이 low 로 잠깐 멈춰도 결과는 같다.
#
#  준비 (PC, mpw_test 폴더에서)
#   mpremote cp out/vectors.bin :vectors.bin
#   mpremote cp vec/stim_bins.csv :stim_bins.csv
#   mpremote run pico/vec_test.py                      (판정만)
#   mpremote run pico/vec_test.py > run_chip01.log     (DUMP_MEASURED=True 일 때 실측 로그까지 저장)
#
#  핀은 smoke_test.py 와 동일:
#   GP17 SSN, GP18 SCLK, GP19 MOSI, GP20 CLK, GP21 RSTN  (출력, 연속 5핀 -> PIO out 한 번에)
#   GP16 MISO, GP22 DONE (입력, PIO in 7핀으로 GP16..22 를 읽고 bit0/bit6 사용)
#   GP15 HCT245 OE (active low)

from machine import Pin
import rp2, time, micropython, array

# =========================== 설정 ===========================
CHIP_ID        = "chip01"
CLK_HZ         = 4_000_000     # i_clk. 100 kHz 로 먼저 전체 PASS 확인 -> 1 MHz -> 최대 4 MHz 정도까지 올려보기
INVERT_INPUTS  = True        # HC14 반전 보상 (smoke_test 와 동일)
VEC_FILE       = "vectors.bin"
BINS_FILE      = "stim_bins.csv"
RUN_BINS       = None        # None = 전부.  예: [0, 1, 3] 처럼 일부만
CHUNK          = 16384       # 한 번에 DMA 로 보내는 벡터 수 (RAM 3 x CHUNK 바이트 사용)
MAX_REPORT     = 8           # bin 당 자세히 출력할 불일치 개수
STOP_ON_FAIL   = False       # True: 첫 FAIL bin 에서 중단 (functional 모드)
DUMP_MEASURED  = False       # True: "M <idx> <miso> <done>" 줄을 전부 출력 -> PC 에서 compare_log.py 로 판정
LOG_TO_FILE    = True        # 요약을 피코 내부 log_vec_<CHIP_ID>.txt 에 append
SM_ID          = 0           # 0~3 = PIO0. (WLAN 을 같이 쓰다가 충돌하면 8 = PIO2 SM0 으로)

# =========================== 핀 ===========================
GP_MISO, GP_SSN, GP_SCLK, GP_MOSI, GP_CLK, GP_RSTN, GP_DONE = 16, 17, 18, 19, 20, 21, 22
GP_OE = 15

PIO_FREQ = CLK_HZ * 32       # PIO 1 사이클 = i_clk 주기 / 32
assert PIO_FREQ <= 150_000_000, "CLK_HZ 최대 4.68 MHz (PIO 32 cycles/vector)"

oe = Pin(GP_OE, Pin.OUT, value=1)       # 버퍼 끈 상태로 시작
Pin(GP_MISO, Pin.IN)
Pin(GP_DONE, Pin.IN)


def _phys(chip_level):
    return (chip_level ^ 1) if INVERT_INPUTS else chip_level


# 벡터 4비트 {rstn,ssn,sclk,mosi} (+ i_clk=0) -> GP17..21 물리 레벨 5비트
#   bit0 GP17 SSN, bit1 GP18 SCLK, bit2 GP19 MOSI, bit3 GP20 CLK, bit4 GP21 RSTN
def _pack(rstn, ssn, sclk, mosi, clk=0):
    return (_phys(ssn) | (_phys(sclk) << 1) | (_phys(mosi) << 2) |
            (_phys(clk) << 3) | (_phys(rstn) << 4))


LUT = bytearray(16)
for v in range(16):
    LUT[v] = _pack((v >> 3) & 1, (v >> 2) & 1, (v >> 1) & 1, v & 1)

IDLE = _pack(0, 1, 0, 0)   # 리셋 유지, SSN high, SCLK low, MOSI low, i_clk low
_OUT_INIT = tuple(rp2.PIO.OUT_HIGH if (IDLE >> b) & 1 else rp2.PIO.OUT_LOW for b in range(5))

# =========================== PIO ===========================
# 한 벡터 = 32 PIO 사이클
#   t=0  i_clk 하강 / t=2 입력 인가 / t=16 i_clk 상승 / t=30 GP16..22 샘플 / t=31 push
#   TX FIFO 가 비면 out 에서 멈춤 -> i_clk 은 low 로 정지 (정적 논리라 안전)
# asm_pio 함수 안에서는 전역 변수를 못 쓰므로 반전 여부별로 두 벌을 둔다.


@rp2.asm_pio(out_init=_OUT_INIT, set_init=rp2.PIO.OUT_HIGH,
             out_shiftdir=rp2.PIO.SHIFT_RIGHT, autopull=True, pull_thresh=5,
             in_shiftdir=rp2.PIO.SHIFT_LEFT)
def player_inv():               # HC14 반전: 칩 i_clk low = 물리 1
    wrap_target()
    set(pins, 1)        [1]     # 칩 i_clk 하강
    out(pins, 5)        [13]    # 입력 인가 (CLK 비트도 같은 값 1 로 유지)
    set(pins, 0)        [13]    # 칩 i_clk 상승
    in_(pins, 7)                # GP16..GP22 샘플 (다음 하강 2사이클 전)
    push(block)
    wrap()


@rp2.asm_pio(out_init=_OUT_INIT, set_init=rp2.PIO.OUT_LOW,
             out_shiftdir=rp2.PIO.SHIFT_RIGHT, autopull=True, pull_thresh=5,
             in_shiftdir=rp2.PIO.SHIFT_LEFT)
def player_noinv():
    wrap_target()
    set(pins, 0)        [1]
    out(pins, 5)        [13]
    set(pins, 1)        [13]
    in_(pins, 7)
    push(block)
    wrap()


_PIO_IDX, _SM_IDX = SM_ID // 4, SM_ID % 4
_PIO_BASE = (0x50200000, 0x50300000, 0x50400000)[_PIO_IDX]
TXF = _PIO_BASE + 0x010 + 4 * _SM_IDX
RXF = _PIO_BASE + 0x020 + 4 * _SM_IDX
DREQ_TX = _PIO_IDX * 8 + _SM_IDX
DREQ_RX = _PIO_IDX * 8 + 4 + _SM_IDX

# =========================== 빠른 루프 (viper) ===========================


@micropython.viper
def _xlat(src: ptr8, dst: ptr8, lut: ptr8, n: int):
    for i in range(n):
        dst[i] = lut[src[i] & 0xF]


@micropython.viper
def _cmp(vec: ptr8, res: ptr8, n: int, rec: ptr32, maxrec: int) -> int:
    # 불일치: rec[k] = (chunk 내 인덱스 << 2) | (miso 불일치 1) | (done 불일치 2)
    nerr = 0
    for i in range(n):
        v = vec[i]
        r = res[i]
        bad = 0
        if v & 0x80:
            if ((v >> 6) ^ r) & 1:
                bad |= 1
        if v & 0x20:
            if ((v >> 4) ^ (r >> 6)) & 1:
                bad |= 2
        if bad:
            if nerr < maxrec:
                rec[nerr] = (i << 2) | bad
            nerr += 1
    return nerr

# =========================== 로그 ===========================
_logf = None


def log(msg):
    print(msg)
    if _logf:
        _logf.write(msg + "\n")


def load_bins(path):
    bins = []
    with open(path) as f:
        f.readline()                                    # header
        for line in f:
            t = line.strip().split(",")
            if len(t) >= 4:
                bins.append((int(t[0]), t[1], int(t[2]), int(t[3])))
    return bins

# =========================== 재생기 ===========================


class Player:
    def __init__(self):
        prog = player_inv if INVERT_INPUTS else player_noinv
        self.sm = rp2.StateMachine(SM_ID, prog, freq=PIO_FREQ,
                                   out_base=Pin(GP_SSN), set_base=Pin(GP_CLK), in_base=Pin(GP_MISO))
        self.tx_dma = rp2.DMA()
        self.rx_dma = rp2.DMA()
        self.tx_ctrl = self.tx_dma.pack_ctrl(size=0, inc_read=True, inc_write=False, treq_sel=DREQ_TX)
        self.rx_ctrl = self.rx_dma.pack_ctrl(size=0, inc_read=False, inc_write=True, treq_sel=DREQ_RX)
        self.sm.restart()
        while self.sm.rx_fifo():
            self.sm.get()
        self.sm.active(1)                               # 첫 out 에서 대기 (i_clk low, 핀 = IDLE)

    def run(self, tx, rx, n):
        rx_dma, tx_dma = self.rx_dma, self.tx_dma
        rx_dma.config(read=RXF, write=rx, count=n, ctrl=self.rx_ctrl, trigger=True)
        tx_dma.config(read=tx, write=TXF, count=n, ctrl=self.tx_ctrl, trigger=True)
        t_ms = n * 1000 // CLK_HZ + 200
        t0 = time.ticks_ms()
        while rx_dma.active():
            if time.ticks_diff(time.ticks_ms(), t0) > t_ms:
                tx_dma.active(0)
                rx_dma.active(0)
                raise RuntimeError("DMA timeout (rx 남은 개수 %d)" % rx_dma.count)

    def close(self):
        self.tx_dma.active(0)
        self.rx_dma.active(0)
        self.sm.active(0)
        self.tx_dma.close()
        self.rx_dma.close()


def safe_idle():
    """PIO 해제 후 칩을 리셋 상태로 두고 버퍼 isolation (smoke_test.stop_all 과 같은 상태)."""
    for gp, b in ((GP_SSN, 0), (GP_SCLK, 1), (GP_MOSI, 2), (GP_CLK, 3), (GP_RSTN, 4)):
        Pin(gp, Pin.OUT, value=(IDLE >> b) & 1)
    time.sleep_ms(1)
    oe.value(1)

# =========================== 메인 ===========================


def main():
    global _logf
    bins = load_bins(BINS_FILE)
    if RUN_BINS is not None:
        bins = [b for b in bins if b[0] in RUN_BINS]
    if LOG_TO_FILE:
        _logf = open("log_vec_%s.txt" % CHIP_ID, "a")

    nvec_total = sum(b[3] - b[2] + 1 for b in bins)
    log("\n##### MyChip_FP_MAC vector test  chip=%s  i_clk=%d Hz  vectors=%d  invert=%s #####"
        % (CHIP_ID, CLK_HZ, nvec_total, INVERT_INPUTS))

    vec = bytearray(CHUNK)
    tx = bytearray(CHUNK)
    rx = bytearray(CHUNK)
    mv_vec = memoryview(vec)
    rec = array.array("I", [0] * MAX_REPORT)
    summary = []
    player = None
    f = open(VEC_FILE, "rb")
    t_start = time.ticks_ms()
    try:
        player = Player()                               # 핀 = IDLE (리셋 유지)
        time.sleep_ms(1)
        oe.value(0)                                     # 버퍼 켬
        time.sleep_ms(1)

        for bid, name, start, end in bins:
            n_miso = n_done = 0
            first = None
            shown = 0
            i = start
            while i <= end:
                n = min(CHUNK, end - i + 1)
                f.seek(i)
                f.readinto(mv_vec[:n])
                _xlat(vec, tx, LUT, n)
                player.run(tx, rx, n)
                nerr = _cmp(vec, rx, n, rec, MAX_REPORT)
                if nerr:
                    # 정확한 miso/done 별 개수
                    for k in range(n):
                        v, r = vec[k], rx[k]
                        if (v & 0x80) and ((v >> 6) ^ r) & 1:
                            n_miso += 1
                        if (v & 0x20) and ((v >> 4) ^ (r >> 6)) & 1:
                            n_done += 1
                    for k in range(min(nerr, MAX_REPORT)):
                        if shown >= MAX_REPORT:
                            break
                        j = rec[k] >> 2
                        v, r = vec[j], rx[j]
                        idx = i + j
                        if first is None:
                            first = idx
                        log("   FAIL idx=%d in{rstn,ssn,sclk,mosi}=%d%d%d%d  exp miso=%d done=%d  got miso=%d done=%d"
                            % (idx, (v >> 3) & 1, (v >> 2) & 1, (v >> 1) & 1, v & 1,
                               (v >> 6) & 1, (v >> 4) & 1, r & 1, (r >> 6) & 1))
                        shown += 1
                if DUMP_MEASURED:
                    out = []
                    for k in range(n):
                        r = rx[k]
                        out.append("M %d %d %d" % (i + k, r & 1, (r >> 6) & 1))
                        if len(out) == 256:
                            print("\n".join(out))
                            out = []
                    if out:
                        print("\n".join(out))
                i += n
            ok = (n_miso == 0 and n_done == 0)
            summary.append((bid, name, ok, first, n_miso, n_done))
            log("bin %2d %-26s %s" % (bid, name, "PASS" if ok else
                                      "FAIL first@%d miso_err=%d done_err=%d" % (first, n_miso, n_done)))
            if not ok and STOP_ON_FAIL:
                log("!! STOP_ON_FAIL")
                break
    finally:
        f.close()
        if player:
            player.close()
        safe_idle()
        dt = time.ticks_diff(time.ticks_ms(), t_start)
        npass = sum(1 for s in summary if s[2])
        log("\n========== SUMMARY (%s, i_clk %d Hz, %.1f s) ==========" % (CHIP_ID, CLK_HZ, dt / 1000))
        log("  %d / %d bins PASS   -> %s" % (npass, len(summary),
                                             "CHIP PASS" if summary and npass == len(summary) and len(summary) == len(bins) else "CHIP FAIL"))
        # compare_log.py 와 같은 형식의 CSV 한 줄 (yield 집계용)
        row = [CHIP_ID] + ["PASS" if s[2] else "FAIL@%d(miso=%d;done=%d)" % (s[3], s[4], s[5]) for s in summary]
        log("CSV," + ",".join(row))
        if _logf:
            _logf.close()
            _logf = None


if __name__ == "__main__":
    main()
