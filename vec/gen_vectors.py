#!/usr/bin/env python3
"""
MyChip_FP_MAC MPW 테스트 벡터 생성기
- 벡터 1줄 = i_clk 1사이클.  형식:  "<rstn><ssn><sclk><mosi>"  (4문자, 0/1)
- bins.csv : bin 번호, 이름, 시작 벡터 인덱스, 끝 인덱스
- 기대값(expect.txt)은 이 파일이 만들지 않는다. 게이트 넷리스트 시뮬(run_gls.sh)이 만든다.

사용:  python3 gen_vectors.py [--K 4] [--G 8] [--seed 1] [--nrand 20] -o stim.txt
"""
import argparse, random, csv, sys

# ---------------- E4M3 / E5M2 인코딩 도우미 ----------------
def enc_e4m3(sign, exp, mant):  # exp: 0..15 (bias 7), mant: 0..7
    return (sign << 7) | (exp << 3) | mant

def enc_e5m2(sign, exp, mant):  # exp: 0..31 (bias 15), mant: 0..3
    return (sign << 7) | (exp << 2) | mant

E4M3_ONE  = enc_e4m3(0, 7, 0)     # 1.0
E4M3_TWO  = enc_e4m3(0, 8, 0)     # 2.0
E4M3_HALF = enc_e4m3(0, 6, 0)     # 0.5
E4M3_ZERO = 0x00
E4M3_NAN  = enc_e4m3(0, 15, 7)
E4M3_MAX  = enc_e4m3(0, 15, 6)    # 448 (E4M3 max normal)
E5M2_ONE  = enc_e5m2(0, 15, 0)
E5M2_INF  = enc_e5m2(0, 31, 0)
E5M2_MAX  = enc_e5m2(0, 30, 3)

CMD_LOAD_W, CMD_LOAD_I, CMD_COMPUTE, CMD_ACC, CMD_READ, CMD_NOP = 0, 1, 2, 3, 4, 7

class VecGen:
    def __init__(self, K=4, G=8):
        self.K = K          # SCLK 반주기 (i_clk 사이클 수)
        self.G = G          # 프레임 사이 SSN high 유지 사이클 수
        self.vec = []       # (rstn, ssn, sclk, mosi)
        self.bins = []      # (bin_id, name, start, end)
        self.marks = []     # (index, comment)  디버깅용

    # --- 원시 연산 ---
    def cyc(self, rstn, ssn, sclk, mosi, n=1):
        for _ in range(n):
            self.vec.append((rstn, ssn, sclk, mosi))

    def idle(self, n):
        self.cyc(1, 1, 0, 0, n)

    def reset(self, n_low=8, n_post=4):
        self.cyc(0, 1, 0, 0, n_low)
        self.cyc(1, 1, 0, 0, n_post)

    def spi_frame(self, cmd, data8=0, addr=0, mode=0, K=None, G=None, mosi_idle=0):
        K = self.K if K is None else K
        G = self.G if G is None else G
        w = ((cmd & 7) << 13) | ((data8 & 0xFF) << 5) | ((addr & 0xF) << 1) | (mode & 1)
        self.cyc(1, 0, 0, mosi_idle, K)                 # SSN low, TBUF 로드 여유
        for b in range(15, -1, -1):
            bit = (w >> b) & 1
            self.cyc(1, 0, 0, bit, K)                   # SCLK low : MOSI 세팅
            self.cyc(1, 0, 1, bit, K)                   # SCLK high: 칩이 MOSI 샘플 / 마스터가 MISO 샘플
        self.cyc(1, 0, 0, mosi_idle, K)
        self.cyc(1, 1, 0, 0, G)                         # SSN high -> rx_done -> 명령 실행

    # --- 매크로 ---
    def load_all(self, W, I, mode_in):
        for a in range(9):
            self.spi_frame(CMD_LOAD_W, W[a], a, mode_in)
        for a in range(9):
            self.spi_frame(CMD_LOAD_I, I[a], a, mode_in)

    def acc_and_read(self, mode_out, wait_acc=24, wait_rd=8):
        self.spi_frame(CMD_ACC)
        self.idle(wait_acc)                             # 누산 완료 대기 (~14사이클 필요)
        self.spi_frame(CMD_READ, 0, 0, mode_out)
        self.idle(wait_rd)                              # r_dat 갱신 대기 (~6사이클 필요)
        self.mark("READOUT")
        self.spi_frame(CMD_NOP)                         # 더미 프레임: MISO로 결과 16비트 클럭아웃

    def mac(self, W, I, mode_in, mode_out):
        self.load_all(W, I, mode_in)
        self.acc_and_read(mode_out)

    # --- bin 관리 ---
    def begin_bin(self, bid, name):
        self._cur = (bid, name, len(self.vec))
        self.reset()

    def end_bin(self):
        bid, name, start = self._cur
        self.bins.append((bid, name, start, len(self.vec) - 1))

    def mark(self, txt):
        self.marks.append((len(self.vec), txt))

    # --- 출력 ---
    def write(self, stim_path, bins_path, marks_path):
        with open(stim_path, "w") as f:
            for r, s, c, m in self.vec:
                f.write(f"{r}{s}{c}{m}\n")
        with open(bins_path, "w", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(["bin", "name", "start", "end", "ncycles"])
            for b in self.bins:
                wr.writerow([b[0], b[1], b[2], b[3], b[3] - b[2] + 1])
        with open(marks_path, "w") as f:
            for i, t in self.marks:
                f.write(f"{i} {t}\n")


def build(K, G, seed, nrand):
    g = VecGen(K, G)
    rnd = random.Random(seed)
    ones = [E4M3_ONE] * 9
    zeros = [E4M3_ZERO] * 9

    # bin 0: 리셋 후 아이들 — MISO가 0으로 유지되는지
    g.begin_bin(0, "reset_idle"); g.idle(32); g.end_bin()

    # bin 1: 아무 명령 없이 더미 프레임 — MISO는 r_dat 리셋값(0)이어야 함
    g.begin_bin(1, "spi_loopback_zero"); g.spi_frame(CMD_NOP, 0xA5, 0xA, 1); g.end_bin()

    # bin 2: READ_RESULT를 ACC 없이 보내면 무시되어야 함 (MISO 0 유지)
    g.begin_bin(2, "read_without_acc")
    g.load_all(ones, ones, 0)
    g.spi_frame(CMD_READ, 0, 0, 0); g.idle(8); g.spi_frame(CMD_NOP)
    g.end_bin()

    # bin 3: 전 원소 1.0*1.0 -> 9.0  (E4M3 out: 9.0 = 1.001 x 2^3 -> exp 10, mant 001 -> 0x51)
    g.begin_bin(3, "all_ones_9"); g.mac(ones, ones, 0, 0); g.end_bin()

    # bin 4: 원소 k 하나만 2.0*2.0=4.0, 나머지 0  (k=0..8) — RF 주소/FPU 그룹/mux 스케줄 분리 검증
    g.begin_bin(4, "single_element_k")
    for k in range(9):
        W = list(zeros); I = list(zeros); W[k] = E4M3_TWO; I[k] = E4M3_TWO
        g.mark(f"k={k}"); g.mac(W, I, 0, 0)
    g.end_bin()

    # bin 5: 덮어쓰기 + ACC 재실행 — RF 재기록, acc_reg 초기화
    g.begin_bin(5, "overwrite_and_rerun")
    g.load_all(ones, ones, 0)
    g.spi_frame(CMD_LOAD_W, E4M3_TWO, 3, 0)           # W[3]=2.0 -> 합 10.0
    g.acc_and_read(0)
    g.acc_and_read(0)                                 # 같은 데이터 재실행 -> 같은 결과
    g.spi_frame(CMD_LOAD_W, E4M3_ZERO, 3, 0)          # W[3]=0 -> 합 8.0
    g.acc_and_read(0)
    g.end_bin()

    # bin 6: READ 두 번 연속 — 두 번째는 acc_done_flag가 지워져 무시되어야 함
    g.begin_bin(6, "double_read")
    g.load_all(ones, ones, 0)
    g.acc_and_read(0)
    g.spi_frame(CMD_READ, 0, 0, 0); g.idle(8); g.spi_frame(CMD_NOP)   # 두 번째 READ (무시) 후 읽기
    g.end_bin()

    # bin 7: 부호/ReLU/상쇄 — 음수 합 -> 0, +a-a -> 0, 부호 섞인 양수 합
    g.begin_bin(7, "sign_relu_cancel")
    neg1 = enc_e4m3(1, 7, 0)
    g.mark("all -1*1 -> ReLU 0");      g.mac([neg1]*9, ones, 0, 0)
    W = [E4M3_TWO, neg1] + [E4M3_ZERO]*7; I = [E4M3_ONE, E4M3_TWO] + [E4M3_ZERO]*7
    g.mark("2-2 -> 0");                g.mac(W, I, 0, 0)
    W = [E4M3_TWO]*5 + [neg1]*4
    g.mark("5*2 - 4*1 = 6");           g.mac(W, ones, 0, 0)
    g.end_bin()

    # bin 8: 특수값/포화 — NaN 전파, 오버플로 포화, 언더플로 플러시
    g.begin_bin(8, "special_values")
    W = list(ones); W[4] = E4M3_NAN
    g.mark("NaN in W[4]");             g.mac(W, ones, 0, 0)
    g.mark("max*max overflow");        g.mac([E4M3_MAX]*9, [E4M3_MAX]*9, 0, 0)
    tiny = enc_e4m3(0, 1, 0)           # 2^-6
    g.mark("tiny*tiny underflow");     g.mac([tiny]*9, [tiny]*9, 0, 0)
    g.mark("E4M3 exp=0 flush");        g.mac([enc_e4m3(0, 0, 7)]*9, ones, 0, 0)
    g.end_bin()

    # bin 9: 라운딩 — 가수가 꽉 찬 값끼리 곱해 라운딩/라운딩 오버플로 경로 자극
    g.begin_bin(9, "rounding")
    full = enc_e4m3(0, 7, 7)           # 1.875
    g.mark("1.875*1.875 x9");          g.mac([full]*9, [full]*9, 0, 0)
    g.mark("1.875*1.0 + ...");         g.mac([full]*9, ones, 0, 0)
    W = [enc_e4m3(0, 7, m) for m in range(8)] + [E4M3_ONE]
    I = [enc_e4m3(0, 7, (7 - m)) for m in range(8)] + [E4M3_ONE]
    g.mark("mant sweep");              g.mac(W, I, 0, 0)
    g.end_bin()

    # bin 10: 지수 차 큰 누산 — 큰 값 + 아주 작은 값 (작은 항 버림 경로)
    g.begin_bin(10, "exp_diff_large")
    W = [enc_e4m3(0, 14, 0)] + [enc_e4m3(0, 2, 0)]*8
    g.mark("2^7 + 8*2^-5");            g.mac(W, ones, 0, 0)
    g.end_bin()

    # bin 11: 모드 4조합 — 입력 E5M2 / 출력 E5M2
    g.begin_bin(11, "modes")
    e5ones = [E5M2_ONE]*9
    g.mark("in=E5M2 out=E4M3");        g.mac(e5ones, e5ones, 1, 0)
    g.mark("in=E4M3 out=E5M2");        g.mac(ones, ones, 0, 1)
    g.mark("in=E5M2 out=E5M2");        g.mac(e5ones, e5ones, 1, 1)
    g.mark("E5M2 inf in");             g.mac([E5M2_INF] + e5ones[1:], e5ones, 1, 1)
    g.mark("E5M2 exp=0 flush");        g.mac([enc_e5m2(0, 0, 3)]*9, e5ones, 1, 1)
    g.mark("E5M2 out overflow");       g.mac([E5M2_MAX]*9, [E5M2_MAX]*9, 1, 1)
    g.end_bin()

    # bin 12: 랜덤 MAC (양수 위주로 결과가 0이 아니게)
    g.begin_bin(12, "random_mac")
    for n in range(nrand):
        mode_in = rnd.randint(0, 1); mode_out = rnd.randint(0, 1)
        def rv():
            if mode_in == 0:
                return enc_e4m3(rnd.randint(0, 1) if rnd.random() < 0.25 else 0, rnd.randint(4, 10), rnd.randint(0, 7))
            return enc_e5m2(rnd.randint(0, 1) if rnd.random() < 0.25 else 0, rnd.randint(12, 18), rnd.randint(0, 3))
        W = [rv() for _ in range(9)]; I = [rv() for _ in range(9)]
        g.mark(f"rand{n} mi={mode_in} mo={mode_out} W={[hex(x) for x in W]} I={[hex(x) for x in I]}")
        g.mac(W, I, mode_in, mode_out)
    g.end_bin()

    # bin 13: 최소 타이밍 — SCLK 반주기 2사이클, 프레임 간격 3사이클 (동기화 마진)
    g.begin_bin(13, "min_timing_K2_G3")
    K0, G0 = g.K, g.G; g.K, g.G = 2, 3
    g.load_all(ones, ones, 0)
    g.acc_and_read(0, wait_acc=16, wait_rd=6)
    g.K, g.G = K0, G0
    g.end_bin()

    # bin 14: 느슨한 타이밍 — 반주기 16, 간격 32
    g.begin_bin(14, "slow_timing_K16_G32")
    K0, G0 = g.K, g.G; g.K, g.G = 16, 32
    g.mac(ones, ones, 0, 0)
    g.K, g.G = K0, G0
    g.end_bin()

    # bin 15: MOSI 아이들 레벨 1 / 무시 명령(101,110) — 원치 않는 상태 천이 없음
    g.begin_bin(15, "ignored_cmds_mosi_high")
    g.load_all(ones, ones, 0)
    g.spi_frame(5, 0xFF, 0xF, 1, mosi_idle=1)
    g.spi_frame(6, 0xFF, 0xF, 1, mosi_idle=1)
    g.spi_frame(CMD_COMPUTE, 0xFF, 0xF, 1)
    g.acc_and_read(0)
    g.end_bin()

    # bin 16: 음수 입력을 모든 위치에 — I/W 부호 비트 latch, 부호 XOR, 뺄셈 경로
    g.begin_bin(16, "negative_inputs_all_pos")
    negI = [enc_e4m3(1, 7, 0)]*9; negW = [enc_e4m3(1, 8, 0)]*9      # -1.0, -2.0
    g.mark("(-2)*(-1) x9 = 18");       g.mac(negW, negI, 0, 0)
    W = [enc_e4m3(0, 8, 0) if k % 2 == 0 else enc_e4m3(1, 8, 0) for k in range(9)]   # +2,-2,+2,...
    I = [enc_e4m3(1, 7, 0) if k % 2 == 0 else enc_e4m3(1, 8, 0) for k in range(9)]   # -1,-2,-1,...
    g.mark("alternating signs");       g.mac(W, I, 0, 0)
    e5negI = [enc_e5m2(1, 15, 0)]*9
    g.mark("E5M2 neg*neg");            g.mac(e5negI, e5negI, 1, 1)
    g.mark("back to positive");        g.mac(ones, ones, 0, 0)     # 부호 래치 1->0 전이
    g.end_bin()

    return g


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--K", type=int, default=4)
    ap.add_argument("--G", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--nrand", type=int, default=20)
    ap.add_argument("-o", "--out", default="stim.txt")
    a = ap.parse_args()
    g = build(a.K, a.G, a.seed, a.nrand)
    base = a.out.rsplit(".", 1)[0]
    g.write(a.out, base + "_bins.csv", base + "_marks.txt")
    print(f"vectors: {len(g.vec)}   bins: {len(g.bins)}")
    for b in g.bins:
        print(f"  bin {b[0]:2d} {b[1]:26s} [{b[2]:7d} .. {b[3]:7d}]  {b[3]-b[2]+1:6d} cyc")
