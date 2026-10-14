#!/usr/bin/env python3
"""
VCD 기반 토글 커버리지 (Cadence IMC 대체)
 - dump.vcd 에서 TOP 스코프의 모든 넷에 대해 0->1, 1->0 전이 횟수를 센다
 - 넷리스트를 파싱해 각 넷을 구동하는 셀 인스턴스/타입을 붙여준다
 - 한 방향이라도 토글 안 한 넷을 인스턴스 이름 접두어(모듈)별로 묶어 보고
사용: python3 toggle_cov.py dump.vcd ../netlist/TOP_new.v [report.txt]
"""
import sys, re, collections

vcd_path, net_path = sys.argv[1], sys.argv[2]
rep_path = sys.argv[3] if len(sys.argv) > 3 else "toggle_report.txt"

# ---------- 1. 넷리스트: 넷 -> (인스턴스, 셀타입, 출력핀) ----------
txt = open(net_path).read()
top = txt[txt.index("module TOP "):]
inst_re = re.compile(r"\n\s+([A-Z][A-Z0-9_]*)\s+(\\?\S+)\s*\((.*?)\);", re.S)
OUT_PINS = {"Y", "Q", "CO", "ck_out"}      # S는 HAX1/FAX1에서만 출력
driver = {}          # net -> (inst, cell, pin)
cells = []
for m in inst_re.finditer(top):
    cell, inst, body = m.group(1), m.group(2).strip(), m.group(3)
    pins = re.findall(r"\.(\w+)\s*\(\s*([^()]*?)\s*\)", body)
    cells.append((inst, cell))
    for pin, net in pins:
        if pin in OUT_PINS or (pin == "S" and cell[:3] in ("HAX", "FAX")):
            net = net.replace(" ", "")
            driver[net] = (inst, cell, pin)
print(f"netlist: {len(cells)} cell instances, {len(driver)} driven nets")

# ---------- 2. VCD 파싱 ----------
id2name = {}
vwidth = {}
scope = []
with open(vcd_path) as f:
    for line in f:
        if line.startswith("$scope"):
            scope.append(line.split()[2])
        elif line.startswith("$upscope"):
            scope.pop()
        elif line.startswith("$var"):
            p = line.split()
            width, vid, name = int(p[2]), p[3], p[4]
            if scope[-1] == "dut":
                id2name.setdefault(vid, []).append((name, width))
                vwidth[vid] = width
        elif line.startswith("$enddefinitions"):
            break
    rise = collections.Counter(); fall = collections.Counter(); cur = {}
    for line in f:
        c = line[0]
        if c in "01xz":
            vid = line[1:].strip(); nv = c
            ov = cur.get(vid)
            if ov == "0" and nv == "1": rise[vid] += 1
            elif ov == "1" and nv == "0": fall[vid] += 1
            cur[vid] = nv
        elif c == "b":
            val, vid = line[1:].split()
            w = vwidth.get(vid)
            if w is None: continue
            pad = val[0] if val[0] in "xz" else "0"      # VCD는 상위 0을 생략 -> 폭 맞춰 확장
            val = pad * (w - len(val)) + val
            ov = cur.get(vid)
            if ov is not None:
                for k, (a, b) in enumerate(zip(ov, val)):
                    key = (vid, len(val) - 1 - k)
                    if a == "0" and b == "1": rise[key] += 1
                    elif a == "1" and b == "0": fall[key] += 1
            cur[vid] = val

# ---------- 3. 넷별 집계 ----------
def norm(name):           # VCD 이름 -> 넷리스트 이름 (\i_data_rf[0] [3] 같은 escaped 이름 처리)
    return name.replace("\\", "").replace(" ", "")

rows = []
for vid, names in id2name.items():
    for name, width in names:
        if width == 1:
            rows.append((norm(name), rise[vid], fall[vid]))
        else:
            for bit in range(width):
                rows.append((norm(f"{name}[{bit}]"), rise[(vid, bit)], fall[(vid, bit)]))

total = len(rows)
full = sum(1 for _, r, f in rows if r and f)
never = [(n, r, f) for n, r, f in rows if not (r and f)]
print(f"nets in VCD: {total}   fully toggled: {full} ({100*full/total:.1f}%)   incomplete: {len(never)}")

def group(net):
    d = driver.get(net)
    inst = d[0] if d else "(port/undriven)"
    inst = inst.lstrip("\\")
    for pfx in ("u_spi", "u_ctrl", "u_acc_r", "u_acc", "u_w_i_rf", "rx_done", "FE_", "CTS_", "RC_CG"):
        if inst.startswith(pfx): return pfx
    return "glue(FPU/ACC_adder/IR/mux 등 평탄화된 조합논리)"

bygrp = collections.defaultdict(list)
for n, r, f in never:
    bygrp[group(n)].append((n, r, f))

with open(rep_path, "w") as o:
    o.write(f"toggle coverage: {full}/{total} nets fully toggled ({100*full/total:.1f}%)\n\n")
    for g in sorted(bygrp, key=lambda k: -len(bygrp[k])):
        o.write(f"== {g}: {len(bygrp[g])} incomplete nets ==\n")
        for n, r, f in sorted(bygrp[g]):
            d = driver.get(n)
            ds = f"{d[1]} {d[0]}.{d[2]}" if d else "-"
            o.write(f"  {n:32s} rise={r:6d} fall={f:6d}   driver: {ds}\n")
        o.write("\n")
print("report ->", rep_path)
for g in sorted(bygrp, key=lambda k: -len(bygrp[k])):
    print(f"  {g:60s} {len(bygrp[g])}")
