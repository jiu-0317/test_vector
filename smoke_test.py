# smoke_test.py
# MyChip_FP_MAC MPW 칩 간단 동작 확인 (Raspberry Pi Pico / MicroPython)
#
#  피코 -> 74HCT245(5V) -> 74HC14(반전) -> 칩 입력 5개
#  피코 <- 74LVC245A(3.3V) <------------ 칩 출력 2개
#
#  칩 입력은 HC14 를 거치며 반전되므로, 이 코드는 "칩이 받는 값" 기준으로 쓰고
#  실제 핀에는 반전해서 내보낸다 (INVERT_INPUTS = True).
#
#  테스트 단계 (각 단계: 받은 값 기록 + 예상값 비교 -> PASS/FAIL)
#   T0 리셋 후 출력 확인          MISO=0, done=0
#   T1 NOP(0xE000)               rx=0x0000, done 0 유지
#   T2 COMPUTE(0x4000)  ★핵심    done -> 1   (SPI 수신 -> IR -> CONTROL 동작)
#   T3 NOP(0xE000)               done -> 0   (새 명령에 클리어)
#   T4 ACC 없이 READ             무시되어 done 0 유지, rx=0x0000
#   T5 최소 MAC (1.0 x 1.0 x 9)  결과 0x0051 (E4M3 9.0)   = 골든 bin 3
#   T6 원소 k 하나만 2.0x2.0     결과 0x0048 (E4M3 4.0) x 9 = 골든 bin 4
#   T7 golden MAC 52케이스        테스트 벡터의 MAC 케이스 전부 (특수값/반올림/E5M2/랜덤/음수)
#   T8 경로 커버 21케이스         연산기 내부 긴 경로를 하나씩 건드리는 케이스
#   T9 랜덤 40케이스              부호 섞임, 가수 꽉 찬 값, E4M3/E5M2
#     (T7~T9 기대값: RTL 비트 정확 모델로 계산 -> RTL + GLS(TOP_new.v) 시뮬과 전부 일치 확인)
#
#  ※ 이 테스트는 SPI 를 느리게(반주기 >= 50 us) 넣으므로, 칩이 실제로 받은 i_clk 가
#    수십 kHz 이상이기만 하면 PASS/FAIL 이 클럭 속도에 거의 영향받지 않는다.
#    고속에서 의미가 있는 건 ACC 9사이클 누산(FPU -> mux -> adder -> acc_reg 루프)이
#    칩 i_clk 로 연속 실행된다는 점뿐이다. CLK_HZ 로 찍히는 값은 칩이 받은 클럭의 증거가 아니다.
#
#  실행: Thonny 에서 열고 Run, 또는  mpremote run smoke_test.py
#  로그: 화면 출력 + 피코 내부 파일 log_<CHIP_ID>.txt (append)

from machine import Pin, PWM
import time

# =========================== 설정 ===========================
CHIP_ID          = "chip01"    # 로그 파일 이름/헤더에 사용
CLK_HZ           = 1_000_000     # i_clk 주파수. 통과 후 1_000_000 으로 올려서 재확인
INVERT_INPUTS    = True        # HC14 반전 보상 (칩 입력 5개)
STOP_ON_CRITICAL = True        # T0/T2 실패 시 뒤 단계 생략
DONE_TIMEOUT_MS  = 20          # done=1 을 기다리는 최대 시간
DONE_HOLD_MS     = 5           # done=0 '유지'를 확인하는 시간
LOG_TO_FILE      = True
RUN_EXTENDED     = True        # T7~T9 실행 (약 5초)
EXT_VERBOSE      = False       # True: T7~T9 도 프레임마다 로그 (느림)

# 칩 SPI 동기화 조건: SCLK 반주기 >= i_clk 4주기, 프레임 간격 >= i_clk 8주기 (여유 2배 이상)
_CYC_US   = 1_000_000 / CLK_HZ
T_HALF_US = max(50, int(8 * _CYC_US) + 1)
GAP_US    = max(100, int(32 * _CYC_US) + 1)
RST_US    = max(1000, int(16 * _CYC_US) + 1)

# =========================== 핀 ===========================
GP_CLK, GP_RSTN, GP_SSN, GP_MOSI, GP_SCLK = 20, 21, 17, 19, 18   # -> HCT245 -> HC14 -> 칩
GP_MISO, GP_DONE = 16, 22                                         # <- LVC245A <- 칩
GP_OE = 15                                                        # HCT245 OE (active low, 반전 없음)

oe = Pin(GP_OE, Pin.OUT, value=1)          # 버퍼 끈 상태로 시작 (칩은 풀 저항으로 안전 상태)


class ChipIn:
    """칩 입력 핀. value 는 '칩이 받는 논리값' 기준."""
    def __init__(self, gp, chip_level):
        self.pin = Pin(gp, Pin.OUT, value=self._phys(chip_level))

    @staticmethod
    def _phys(v):
        return (v ^ 1) if INVERT_INPUTS else v

    def __call__(self, v):
        self.pin.value(self._phys(v))


rstn = ChipIn(GP_RSTN, 0)   # 리셋 유지
ssn  = ChipIn(GP_SSN, 1)    # 선택 안 됨
sclk = ChipIn(GP_SCLK, 0)   # mode 0 idle low
mosi = ChipIn(GP_MOSI, 0)
miso = Pin(GP_MISO, Pin.IN)
done = Pin(GP_DONE, Pin.IN)
clk  = None

# =========================== 명령 워드 ===========================
CMD_LOAD_W, CMD_LOAD_I, CMD_COMPUTE, CMD_ACC, CMD_READ, CMD_NOP = 0, 1, 2, 3, 4, 7
E4M3_ONE, E4M3_TWO, E4M3_ZERO = 0x38, 0x40, 0x00


def word(cmd, data8=0, addr=0, mode=0):
    # [15:13] cmd | [12:5] data8 | [4:1] addr | [0] mode
    return ((cmd & 7) << 13) | ((data8 & 0xFF) << 5) | ((addr & 0xF) << 1) | (mode & 1)


NOP = word(CMD_NOP)          # 0xE000
COMPUTE = word(CMD_COMPUTE)  # 0x4000
ACC = word(CMD_ACC)          # 0x6000
READ_E4M3 = word(CMD_READ)   # 0x8000


def e4m3_to_float(b):
    s, e, m = (b >> 7) & 1, (b >> 3) & 0xF, b & 7
    if e == 15 and m == 7:
        return float("nan")
    v = (m / 8) * 2 ** -6 if e == 0 else (1 + m / 8) * 2 ** (e - 7)
    return -v if s else v


def e5m2_to_float(b):
    s, e, m = (b >> 7) & 1, (b >> 2) & 0x1F, b & 3
    if e == 31:
        return float("nan") if m else (-1) ** s * float("inf")
    v = (m / 4) * 2 ** -14 if e == 0 else (1 + m / 4) * 2 ** (e - 15)
    return -v if s else v

# =========================== 로그 / 판정 ===========================
_logf = None
results = {}      # test -> [n_pass, n_check]


def log(msg):
    print(msg)
    if _logf:
        _logf.write(msg + "\n")


def check(test, label, tx, rx, exp_rx, d, exp_d):
    """한 프레임(또는 한 관찰)의 결과를 기록하고 예상값과 비교."""
    ok = True
    if exp_rx is not None and rx != exp_rx:
        ok = False
    if exp_d is not None and d != exp_d:
        ok = False
    r = results.setdefault(test, [0, 0])
    r[1] += 1
    r[0] += 1 if ok else 0
    tx_s = "  ----" if tx is None else "0x%04X" % tx
    rx_s = "0x%04X" % rx
    erx_s = "  ----" if exp_rx is None else "0x%04X" % exp_rx
    ed_s = "-" if exp_d is None else str(exp_d)
    line = "%-3s %-14s tx=%s  rx=%s (exp %s)  done=%d (exp %s)  %s" % (
        test, label, tx_s, rx_s, erx_s, d, ed_s, "PASS" if ok else "FAIL")
    if not ok and exp_rx is not None and rx != exp_rx:
        line += "\n      rx  bin %s\n      exp bin %s" % (_bin16(rx), _bin16(exp_rx))
    log(line)
    return ok


def _bin16(v):
    s = ""
    for b in range(15, -1, -1):
        s += "1" if (v >> b) & 1 else "0"
        if b == 8:
            s += "_"
    return s


def passed(test):
    r = results.get(test)
    return r is not None and r[0] == r[1]

# =========================== 칩 제어 ===========================


def start_clock():
    global clk
    clk = PWM(Pin(GP_CLK))
    clk.freq(CLK_HZ)
    clk.duty_u16(32768)


def stop_all():
    """테스트 종료: 칩을 리셋 상태로 두고 버퍼 isolation."""
    rstn(0)
    ssn(1)
    sclk(0)
    mosi(0)
    time.sleep_us(RST_US)
    oe.value(1)
    if clk:
        clk.deinit()


def reset():
    rstn(0)
    ssn(1)
    sclk(0)
    mosi(0)
    time.sleep_us(RST_US)
    rstn(1)
    time.sleep_us(RST_US)


def frame(w):
    """16비트 SPI mode 0, MSB first. 보낸 워드 w, 받은 MISO 16비트를 반환."""
    rx = 0
    ssn(0)
    time.sleep_us(T_HALF_US)                 # 칩이 SSN 하강 감지 + TBUF 로드
    for b in range(15, -1, -1):
        mosi((w >> b) & 1)                   # SCLK low 구간: MOSI 세팅
        time.sleep_us(T_HALF_US)
        rx = (rx << 1) | miso.value()        # SCLK 상승 직전에 MISO 샘플
        sclk(1)                              # 칩이 상승엣지에서 MOSI 샘플
        time.sleep_us(T_HALF_US)
        sclk(0)                              # 칩이 하강엣지에서 다음 MISO 비트 시프트
    time.sleep_us(T_HALF_US)
    mosi(0)
    ssn(1)                                   # SSN 상승 -> 명령 실행
    time.sleep_us(GAP_US)
    return rx


def wait_done(expect):
    """expect=1: timeout 안에 1이 되면 1.  expect=0: HOLD 동안 한 번이라도 1이면 1."""
    if expect:
        t0 = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), t0) < DONE_TIMEOUT_MS:
            if done.value():
                return 1
        return 0
    t0 = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), t0) < DONE_HOLD_MS:
        if done.value():
            return 1
    return 0


def send(test, label, w, exp_rx, exp_d):
    rx = frame(w)
    d = wait_done(exp_d) if exp_d is not None else done.value()
    return check(test, label, w, rx, exp_rx, d, exp_d), rx


def load_all(test, W, I, mode=0, exp_rx=0):
    ok = True
    for a in range(9):
        ok &= send(test, "LOAD_W[%d]" % a, word(CMD_LOAD_W, W[a], a, mode), exp_rx, 1)[0]
    for a in range(9):
        ok &= send(test, "LOAD_I[%d]" % a, word(CMD_LOAD_I, I[a], a, mode), exp_rx, 1)[0]
    return ok


def mac(test, W, I, exp_result, exp_rx_before=0):
    """W/I 18개 로드 -> ACC -> READ(E4M3) -> NOP 로 결과 읽기."""
    load_all(test, W, I, 0, exp_rx_before)
    send(test, "ACC", ACC, exp_rx_before, 1)
    send(test, "READ", READ_E4M3, exp_rx_before, 1)
    ok, rx = send(test, "RESULT(NOP)", NOP, exp_result, 0)
    log("      result8=0x%02X -> E4M3 %s   (expected 0x%02X -> %s)" % (
        rx & 0xFF, e4m3_to_float(rx & 0xFF), exp_result & 0xFF, e4m3_to_float(exp_result & 0xFF)))
    return ok

# =========================== 테스트 단계 ===========================


def t0():
    log("\n[T0] 리셋 후 출력 확인")
    reset()
    time.sleep_ms(1)
    return check("T0", "after reset", None, miso.value(), 0, done.value(), 0)


def t1():
    log("\n[T1] NOP -> 응답 0, done 0 유지")
    return send("T1", "NOP", NOP, 0x0000, 0)[0]


def t2():
    log("\n[T2] COMPUTE -> done 1 (칩 생존 확인)")
    return send("T2", "COMPUTE", COMPUTE, 0x0000, 1)[0]


def t3():
    log("\n[T3] NOP -> done 0 으로 클리어")
    return send("T3", "NOP", NOP, 0x0000, 0)[0]


def t4():
    log("\n[T4] ACC 없이 READ -> 무시")
    send("T4", "READ", READ_E4M3, 0x0000, 0)
    return send("T4", "NOP", NOP, 0x0000, 0)[0]


def t5():
    log("\n[T5] 최소 MAC: 1.0 x 1.0 x 9 = 9.0 -> 0x0051")
    reset()
    return mac("T5", [E4M3_ONE] * 9, [E4M3_ONE] * 9, 0x0051, 0x0000)


def t6():
    log("\n[T6] 원소 k 하나만 2.0 x 2.0 = 4.0 -> 0x0048 (k=0..8)")
    reset()
    n_ok = 0
    for k in range(9):
        log("  -- k=%d" % k)
        W = [E4M3_ZERO] * 9
        I = [E4M3_ZERO] * 9
        W[k] = E4M3_TWO
        I[k] = E4M3_TWO
        # k>=1 이면 LOAD 프레임 MISO 에 직전 결과(0x0048)가 반복 출력되는 게 정상 -> 비교 안 함
        before = 0x0000 if k == 0 else None
        tag = "T6k%d" % k
        if mac(tag, W, I, 0x0048, before) and passed(tag):
            n_ok += 1
    results["T6"] = [n_ok, 9]
    return n_ok == 9


# =========================== 확장 테스트 (T7~T9) ===========================
# 한 줄 = W[0..8] I[0..8] (hex 36자) | mode_in | mode_out | 기대 결과 8비트(hex)
#  - 연속된 두 케이스의 기대값은 항상 다르게 배치 (READ/ACC 프레임이 빠지면 직전 결과가 나와 FAIL 로 잡힘)
#  - T8/T9 는 결과가 0 이 아닌 케이스만 (0 이면 ReLU 에 가려져 내부 오류가 안 보임)
#  - 생성: gen_smoke_cases.py / order_and_embed.py
CASES = {
    "T7": """
000040000000000000000040000000000000 0 0 48
c1363c3e48303e3b3f3e31393b42464bbf35 1 1 51
004000000000000000004000000000000000 0 0 48
080808080808080808080808080808080808 0 0 00
000000400000000000000000400000000000 0 0 48
4832a042d1282c533d333640464e24492256 0 0 00
3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c 1 1 48
383838383838383838383838383838383838 0 0 51
383838383838383838383838383838383838 0 1 48
3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c 1 0 51
400000000000000000400000000000000000 0 0 48
0303030303030303033c3c3c3c3c3c3c3c3c 1 1 00
000000004000000000000000004000000000 0 0 48
2a554c2853c2313e4738322620422c36292d 0 1 51
000000000000000040000000000000000040 0 0 48
070707070707070707383838383838383838 0 0 00
000000000040000000000000000040000000 0 0 48
383838383838383838383838383838383838 0 0 51
000000000000004000000000000000004000 0 0 48
323a3e41433d373c3e323e4a41364b3b4131 1 0 64
4040404040b8b8b8b8383838383838383838 0 0 4c
473646493e33c531493a38494133413f3ebc 1 0 69
000000000000400000000000000000400000 0 0 48
b8b8b8b8b8b8b8b8b8383838383838383838 0 0 00
3f3f3f3f3f3f3f3f3f383838383838383838 0 0 58
c0c0c0c0c0c0c0c0c0b8b8b8b8b8b8b8b8b8 0 0 59
2954205452224c373fbd2c462322462f3d38 0 0 57
3a244e4f494c2bb1b8b33a3533263b292f4a 0 1 4b
bcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbc 1 1 48
7c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c 1 1 7d
353e3d463e31493f4a313f35bfbb344b3e3d 1 1 59
40b800000000000000384000000000000000 0 0 00
3e48b936413a3a3e364732353f3534484442 1 0 5d
2c443157303a3156413427202050a94b3e44 0 0 62
394a26233026494c5326b727c3bc4b45204d 0 0 6a
40c040c040c040c040b8c0b8c0b8c0b8c0b8 0 0 4c
364a3b3cc34b39394ab23e3a404938304a49 1 1 57
7b7b7b7b7b7b7b7b7b7b7b7b7b7b7b7b7b7b 1 1 7b
38393a3b3c3d3e3f383f3e3d3c3b3a393838 0 0 58
532ed733472e334936c7a538c8544d444644 0 0 52
701010101010101010383838383838383838 0 0 70
57253a57a424a42c51312b3647c0542d3129 0 0 69
c74742344a3a4ac043bd443e493044314037 1 0 64
383838387f38383838383838383838383838 0 0 7f
4a343a47b944303638b9b838494a47433630 1 1 55
383838383838383838383838383838383838 0 0 51
ba3bbd393f463d333e4045463d3e48403b42 1 0 65
7e7e7e7e7e7e7e7e7e7e7e7e7e7e7e7e7e7e 0 0 7e
3f3b56503325483b4857434b3041a54e4b47 0 0 72
4d35482d353c3620c44d553d28422e40442c 0 1 54
bd3db23c43313541423d3f493d304249c246 1 1 4b
3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f 0 0 60
""",
    "T8": """
4747cf3f3fc73fcfbf473fb7b72f4f4fafc7 0 0 5c
0b683e61be6c736c6139e3405d926225f805 1 0 78
e06429304b132cde926d6e72536d0b08591a 1 1 5c
40bdb7bbb93f3b36313f37384bba45ba4446 1 0 40
374747bf47af4f2fc7b74fcf4f474f4f2f2f 0 0 64
37cf4f4faf4f2f37372f4f4faf3f2f472f3f 0 0 45
20b54747bc3342b8c1473329b529463cad3d 0 0 2c
cf37c7af3f37474f4fbf4f3f2fcf2f4f3747 0 0 68
bab42d3c30422153352b22272aa2a1445243 0 0 6e
b738bcb0be4744453c383838383838383838 0 0 50
bfb73f3f373fcfcf2f373fcf3f374f4fcf47 0 1 41
2935f8985c498a723236097a613e3de05765 1 1 60
4f4fbf2f4737cf474f2f2f472f3f2f4fbf4f 0 0 30
2217443e5e1ba86c1949213baff2c9f165e7 1 1 5c
6e6939964453df5b743046f9603141c3a599 0 0 6a
20b84e53374047c5b7a1523cb42c484a4bb5 0 1 3c
67234de1d0f98c0f287b587b9957502bf137 1 0 78
""",
    "T9": """
3dad50d2d54225a05720244a412f34513253 0 1 59
84dfd98ee2327a4c4822a50a19d79a5bf947 1 1 6c
a9d43845ce57263730523554c0c428b33347 0 0 59
47372fbf4f47afbfc7373fcfb74f472f3737 0 0 69
a9423f4c4237cb43d04caf532448ca314c41 0 0 59
4647bcb2bc40be3a33453f373c43bac23034 1 0 62
3810cdc268f396777665726058721935cb55 0 1 72
3b8af42912cc0e14161586955c49bb37e81f 1 0 62
48423d32c2424bbd34b5313448413b47ba47 1 0 6c
c0423733bd36c9b6c743b2b63e3340c83843 1 0 64
a0542b453313d72816201857b94f16365c7a 0 0 59
37afc73f4f473f4fb7474f2f4faf47b74f4f 0 0 69
474f373fb7af4747c7af37474fb747372f37 0 0 5c
1a371a1260360f219776471ead1d269253ab 0 0 5d
5c7212d5a07d75b54c7f317a3748884ecc61 0 1 72
4024e81cd136c656733c543c433a4112463e 0 0 78
4fcf37af3f3f3f47373f2fcf37cf3f473faf 0 0 4c
155344a31727565ebb17276279385b313112 1 1 69
af3f47bf2f4f3737b73f3f2f474f47bfbf4f 0 0 59
d972064139d2715d6a936b74c2654d40d810 1 1 76
c23732c1bdb848beb9b243bd3334b03b4030 1 0 4a
47472f474f3f373fcf4f4fbf4f2f2f474faf 0 1 57
44234e3acad340d02c2fd15255a9b84b4e2d 0 0 66
47474f47373fc7cf472f4747afcf3f4f3f4f 0 0 5c
d4cd289e62323d3b238b454732a85c0a644f 0 1 52
313c43d149482a25b23b3338404522513723 0 1 45
bd3bbd4538c23ec4c734313db5b1bc3ecab3 1 0 65
05043a4cac30472f9208a61657558560bf36 1 1 6d
292e545d5469775f5ac96969486d9eab76e3 1 1 6c
b5b2c9d44f375456afb0523ec355345132a2 0 0 77
ef3597a42669962f192299d46c2c19137808 0 0 6b
4030babf4b4641bec6383cb04446493a4931 1 0 6f
37305b57512796454413559f04391804884f 1 0 71
990912d8be3485cd9959950a10bd622b077b 1 0 64
33b132bab738424035b934ba48393b4532b3 1 0 51
37af373fcf4f47bf2f4f4f474fc72fbf2fbf 0 0 63
5e435f587727fd522fdb7061241b263821df 0 1 5d
40b7434f435640b2365120c825c9242ab34f 0 0 4d
4647b43b3d303035373941344a47c8bcb038 1 0 62
cd4a544fa728232dce36545356b053213b3b 0 0 79
""",
}

EXT_DESC = {
    "T7": "golden MAC (테스트 벡터 케이스 전부)",
    "T8": "경로 커버 (상쇄 후 정규화 시프트 0~7, 지수차 0~8+, 반올림 캐리, 포화/언더플로)",
    "T9": "랜덤 (부호 섞임, 가수 꽉 찬 값, E4M3/E5M2)",
}


def _parse(txt):
    out = []
    for line in txt.split("\n"):
        t = line.split()
        if len(t) != 4:
            continue
        h = t[0]
        v = [int(h[2 * k:2 * k + 2], 16) for k in range(18)]
        out.append((v[:9], v[9:], int(t[1]), int(t[2]), int(t[3], 16)))
    return out


def _fmt(vals):
    return " ".join("%02x" % x for x in vals)


def mac_case(test, n, W, I, mi, mo, exp8, prev):
    """케이스 1개: LOAD_W x9, LOAD_I x9, ACC, READ(mode_out), NOP(결과 읽기).
    결과 앞 20프레임의 MISO 는 직전에 읽은 결과(prev) 그대로여야 한다 (r_dat 는 READ 처리 후에만 바뀜)."""
    words = [word(CMD_LOAD_W, W[a], a, mi) for a in range(9)]
    words += [word(CMD_LOAD_I, I[a], a, mi) for a in range(9)]
    words += [ACC, word(CMD_READ, 0, 0, mo)]
    stale_bad = 0
    for w in words:
        rx = frame(w)
        if rx != prev:
            stale_bad += 1
        if EXT_VERBOSE:
            log("      tx=0x%04X rx=0x%04X (exp 0x%04X)" % (w, rx, prev))
    rx = frame(NOP)
    d = wait_done(0)
    ok = (rx == exp8) and d == 0 and stale_bad == 0
    r = results.setdefault(test, [0, 0])
    r[1] += 1
    r[0] += 1 if ok else 0
    fmt_out = e4m3_to_float if mo == 0 else e5m2_to_float
    line = "%s #%-3d in=%s out=%s  result=0x%02X (exp 0x%02X = %s)%s  %s" % (
        test, n, "E5M2" if mi else "E4M3", "E5M2" if mo else "E4M3", rx & 0xFF, exp8,
        fmt_out(exp8), "" if stale_bad == 0 else "  stale_miso_err=%d" % stale_bad,
        "PASS" if ok else "FAIL")
    if not ok:
        line += "\n      W=%s\n      I=%s" % (_fmt(W), _fmt(I))
        if rx != exp8:
            line += "\n      rx  bin %s\n      exp bin %s" % (_bin16(rx), _bin16(exp8))
        if d:
            line += "\n      done 이 0 으로 안 내려감"
    log(line)
    return ok, rx


def run_ext(test):
    log("\n[%s] %s" % (test, EXT_DESC[test]))
    reset()                                   # r_dat = 0 에서 시작
    prev = 0x0000
    n_ok = 0
    cases = _parse(CASES[test])
    for n, (W, I, mi, mo, e) in enumerate(cases):
        ok, rx = mac_case(test, n, W, I, mi, mo, e, prev)
        if ok:
            n_ok += 1
        prev = rx              # 다음 케이스의 "직전 결과" = 실제로 읽은 값 (오류 연쇄 방지)
    return n_ok == len(cases)

# =========================== 메인 ===========================


def summary():
    log("\n========== SUMMARY (%s, i_clk %d Hz) ==========" % (CHIP_ID, CLK_HZ))
    for t in ("T0", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9"):
        r = results.get(t)
        if r is None:
            log("  %s  SKIP" % t)
        elif t == "T6":
            log("  %s  %s  (%d/%d k PASS)" % (t, "PASS" if r[0] == r[1] else "FAIL", r[0], r[1]))
        elif t in CASES:
            log("  %s  %s  (%d/%d cases)" % (t, "PASS" if r[0] == r[1] else "FAIL", r[0], r[1]))
        else:
            log("  %s  %s  (%d/%d checks)" % (t, "PASS" if r[0] == r[1] else "FAIL", r[0], r[1]))


def main():
    global _logf
    if LOG_TO_FILE:
        _logf = open("log_%s.txt" % CHIP_ID, "a")
    log("\n##### MyChip_FP_MAC smoke test  chip=%s  i_clk=%d Hz  T_half=%d us  gap=%d us  invert=%s #####"
        % (CHIP_ID, CLK_HZ, T_HALF_US, GAP_US, INVERT_INPUTS))
    try:
        # 전원 순서: OE=1(버퍼 끔) 상태에서 칩 기본값 설정 -> 클럭 시작 -> OE=0 -> 리셋
        start_clock()
        try:
            log("PWM 실제 설정 주파수 = %d Hz (칩 핀에 도달한 클럭은 스코프로 확인)" % clk.freq())
        except Exception:
            pass
        time.sleep_ms(1)
        oe.value(0)
        time.sleep_ms(1)

        if not t0() and STOP_ON_CRITICAL:
            log("!! T0 실패: 리셋/전원/출력 경로를 먼저 확인하세요.")
            return
        t1()
        if not t2() and STOP_ON_CRITICAL:
            log("!! T2 실패: 칩 핀에서 idle 레벨(ssn=5V, sclk=0V, rstn=5V)과 i_clk 를 확인하세요.")
            return
        t3()
        t4()
        t5()
        t6()
        if RUN_EXTENDED:
            for t in ("T7", "T8", "T9"):
                run_ext(t)
    finally:
        summary()
        stop_all()
        if _logf:
            _logf.close()
            _logf = None


if __name__ == "__main__":
    main()
