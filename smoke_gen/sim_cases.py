"""케이스 json -> 스팀(gen_vectors 와 같은 프레임) -> iverilog(RTL/GLS) -> READOUT 결과를 모델 기대값과 비교"""
import sys, json, subprocess, random
sys.path.insert(0, "vec")
import gen_vectors as gv
from model import mac
cases = json.load(open(sys.argv[1]))
nextra = int(sys.argv[2]) if len(sys.argv) > 2 else 0
r = random.Random(7)
for n in range(nextra):          # 모델 검증용 추가 랜덤
    mi = r.randint(0, 1)
    def v():
        if mi == 0:
            return (r.randint(0,1)<<7)|(r.randint(1,15)<<3)|r.randint(0,7)
        return (r.randint(0,1)<<7)|(r.randint(1,30)<<2)|r.randint(0,3)
    W=[v() for _ in range(9)]; I=[v() for _ in range(9)]; mo=r.randint(0,1)
    cases.append({"tag":"extra","W":W,"I":I,"mi":mi,"mo":mo,"exp":mac(W,I,mi,mo)})
g = gv.VecGen(4, 8)
g.reset()
for c in cases:
    g.mac(c["W"], c["I"], c["mi"], c["mo"])
g.write("sim/cases_stim.txt", "sim/cases_bins.csv", "sim/cases_marks.txt")
stim = ["%d%d%d%d" % v for v in g.vec]
reads = [i for i, t in g.marks if t == "READOUT"]
assert len(reads) == len(cases)
for mode in sys.argv[3:] if len(sys.argv) > 3 else ["rtl"]:
    if mode == "rtl":
        cmd = "cd sim && iverilog -g2012 -DRTL -o c_rtl.vvp tb_vec.v ../rtl/*.v && vvp c_rtl.vvp +stim=cases_stim.txt +expect=c_exp_rtl.txt +trace=/dev/null >/dev/null"
        ef = "sim/c_exp_rtl.txt"
    else:
        cmd = "cd sim && iverilog -g2012 -Dno_power_gate -o c_gls.vvp tb_vec.v ../netlist/TOP_new.v ../lib/scl_sim.v && vvp c_gls.vvp +stim=cases_stim.txt +expect=c_exp_gls.txt +trace=/dev/null >/dev/null"
        ef = "sim/c_exp_gls.txt"
    subprocess.run(cmd, shell=True, check=True)
    exp = {}
    for l in open(ef):
        p = l.split(); exp[int(p[0])] = (p[1], p[2])
    def word(i):
        while stim[i][1] != '0': i += 1
        bits = []; prev = '0'
        while stim[i][1] == '0':
            if stim[i][2] == '1' and prev == '0': bits.append(exp[i][0])
            prev = stim[i][2]; i += 1
        return int("".join(bits), 2)
    nx = sum(1 for v in exp.values() if 'x' in v)
    bad = 0
    for c, i in zip(cases, reads):
        w = word(i)
        if w != c["exp"]:
            bad += 1
            if bad < 10: print(mode, "MISMATCH", c, hex(w))
    print("%s: %d cases, vectors %d, x=%d, mismatch=%d" % (mode, len(cases), len(stim), nx, bad))
