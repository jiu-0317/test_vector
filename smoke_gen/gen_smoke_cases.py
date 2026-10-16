"""smoke_test 용 MAC 케이스 생성
 1) golden : gen_vectors.py 의 mac() 케이스 전부 (GLS 로 검증된 것과 같은 데이터)
 2) cover  : 연산기 내부 경로(정규화 시프트 깊이, 지수차, 반올림 캐리, 포화 등)를 하나씩 건드리는 케이스
 3) random : 무작위 (양/음 섞임, 가수 꽉 찬 값 포함)
 기대값은 model.py (RTL 비트 정확 모델, GLS/RTL 로 검증) 로 계산
"""
import random, sys, json
sys.path.insert(0, "vec")
import gen_vectors as gv
from model import mac

# ---------- 1) golden ----------
golden = []
_orig_mac = gv.VecGen.mac


def _rec(self, W, I, mi, mo):
    golden.append((list(W), list(I), mi, mo))
    return _orig_mac(self, W, I, mi, mo)


gv.VecGen.mac = _rec
gv.build(4, 8, 1, 20)
gv.VecGen.mac = _orig_mac


def e4(s, e, m):
    return (s << 7) | (e << 3) | m


def e5(s, e, m):
    return (s << 7) | (e << 2) | m


rnd = random.Random(2026)


def gen_value(kind):
    if kind == "e4":
        return e4(rnd.randint(0, 1), rnd.randint(4, 10), rnd.randint(0, 7))
    if kind == "e4full":
        return e4(rnd.randint(0, 1), rnd.randint(5, 9), 7)
    if kind == "e4wide":
        return e4(rnd.randint(0, 1), rnd.randint(1, 15), rnd.randint(0, 7))
    if kind == "e5":
        return e5(rnd.randint(0, 1), rnd.randint(12, 18), rnd.randint(0, 3))
    if kind == "e5wide":
        return e5(rnd.randint(0, 1), rnd.randint(1, 30), rnd.randint(0, 3))


def gen_value_s(kind):
    v = gen_value(kind)
    # 음수는 25% 만: 최종 합이 양수여야 결과가 ReLU 로 0 이 되지 않고 관측된다
    return (v & 0x7F) | ((1 << 7) if rnd.random() < 0.3 else 0)


def gen_case(kind):
    mi = 1 if kind.startswith("e5") else 0
    mo = 0 if rnd.random() < 0.75 else 1      # E4M3 출력이 가수 비트가 많아 오류가 더 잘 보인다
    if kind == "cancel":
        # I = 1.0 로 두고 W 끼리 거의 같은 크기를 +,- 로 쌓아 깊은 상쇄 유도
        mi = 0
        I = [e4(0, 7, 0)] * 9
        W = []
        for k in range(9):
            e = rnd.randint(6, 8)
            W.append(e4(k & 1, e, rnd.randint(0, 7)))
        rnd.shuffle(W)
        return W, I, mi, mo
    W = [gen_value_s(kind) for _ in range(9)]
    I = [gen_value_s(kind) for _ in range(9)]
    return W, I, mi, mo


def cov(case):
    st = set()
    r = mac(*case, st=st)
    return st, r


# ---------- 2) coverage-driven ----------
universe = {}
pool = []
kinds = ["e4", "e4full", "e4wide", "e5", "e5wide", "cancel"]
MASKED = {0x00, 0x7E, 0x7F, 0x7B, 0x7D}   # 0(ReLU/언더플로), E4M3 max/NaN, E5M2 max/NaN
SAT_POINTS = {"fpu_sat", "add_ovf"}      # 이 포인트는 포화가 목적이라 포화 결과 허용


def observable(r):
    return r != 0          # 0 은 ReLU/언더플로로 가려져 내부 오류를 볼 수 없다


def strict(r):
    return r not in MASKED  # 포화/NaN 결과도 내부 오류를 가린다


for n in range(120000):
    c = gen_case(kinds[n % len(kinds)])
    st, r = cov(c)
    if not observable(r):
        continue
    pool.append((c, st, r))
    for p in st:
        universe[p] = universe.get(p, 0) + 1

covered = {}
for c in golden:
    for p in cov(c)[0]:
        covered[p] = covered.get(p, 0) + 1

PER_POINT = 3
DEEP = {"sub_lz4", "sub_lz5", "sub_lz6", "sub_lz7", "add_unf", "sub_exact_zero", "accr_m0_ru1_c1", "fpu_round_ovf"}


def need(p):
    return 6 if p in DEEP else PER_POINT


cover_cases = []
# 드문 포인트부터 채운다
for p in sorted(universe, key=lambda x: universe[x]):
    while covered.get(p, 0) < need(p):
        cand = [x for x in pool if p in x[1] and (p in SAT_POINTS or strict(x[2]))]
        if not cand:
            break
        # 아직 덜 채워진 포인트를 많이 건드리는 후보 우선
        best = max(cand, key=lambda x: sum(1 for q in x[1] if covered.get(q, 0) < need(q)))
        pool.remove(best)
        cover_cases.append(best[0])
        for q in best[1]:
            covered[q] = covered.get(q, 0) + 1

# ---------- 3) random ----------
rand_cases = []
while len(rand_cases) < 40:
    c = gen_case(kinds[len(rand_cases) % 5])
    if strict(mac(*c)):
        rand_cases.append(c)

out = []
for tag, lst in (("golden", golden), ("cover", cover_cases), ("random", rand_cases)):
    for c in lst:
        out.append({"tag": tag, "W": c[0], "I": c[1], "mi": c[2], "mo": c[3], "exp": mac(*c)})

json.dump(out, open("smoke_cases.json", "w"))
print("cases:", len(out), " golden", len(golden), " cover", len(cover_cases), " random", len(rand_cases))
print("coverage points:", len(universe))
import collections
print("masked(0/sat/nan):", {t: sum(1 for o in out if o['tag'] == t and o['exp'] in MASKED) for t in ('golden', 'cover', 'random')})
for p in sorted(universe):
    print("  %-18s pool_hits=%6d  in_set=%d" % (p, universe[p], covered.get(p, 0) +
          sum(1 for c in rand_cases if p in cov(c)[0])))
