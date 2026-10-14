#!/usr/bin/env python3
"""FPGA가 캡처한 실측 로그를 기대값과 비교해 bin별 pass/fail을 낸다 (yield 모드 집계용)
 기대/실측 로그 형식: 한 줄에 "<idx> <miso> <cmd_done>"  (expect.txt와 같은 형식)
 기대값이 'x' 인 비트는 don't-care. 실측 로그에 없는 idx 는 판정 제외.
사용: python3 compare_log.py expect.txt measured.txt stim_bins.csv [chip_id] >> yield.csv
 stdout: CSV 한 줄 (chip_id, bin별 PASS / FAIL@첫인덱스(miso불일치,done불일치))
 stderr: 사람이 읽는 bin별 요약
"""
import sys, csv

def load(p):
    d = {}
    for l in open(p):
        t = l.split()
        if len(t) >= 3: d[int(t[0])] = (t[1], t[2])
    return d

exp, meas = load(sys.argv[1]), load(sys.argv[2])
bins = list(csv.DictReader(open(sys.argv[3])))
chip = sys.argv[4] if len(sys.argv) > 4 else "chip?"
row = [chip]
for b in bins:
    s, e = int(b["start"]), int(b["end"])
    first = None; nm = nd = 0
    for i in range(s, e + 1):
        if i not in exp or i not in meas: continue
        (xm, xd), (mm, md) = exp[i], meas[i]
        bad = False
        if xm in "01" and mm != xm: nm += 1; bad = True
        if xd in "01" and md != xd: nd += 1; bad = True
        if bad and first is None: first = i
    ok = (nm == 0 and nd == 0)
    row.append("PASS" if ok else f"FAIL@{first}(miso={nm};done={nd})")
    sys.stderr.write(f"bin {b['bin']:>2} {b['name']:26s} "
                     f"{'PASS' if ok else f'FAIL first@{first} miso_err={nm} done_err={nd}'}\n")
print(",".join(row))
