#!/usr/bin/env python3
"""stim + expect(or 실측 로그)에서 SPI 프레임마다 MISO 16비트 워드를 복원해 보여준다.
   - 마스터 샘플 시점 = SCLK 0->1 되는 벡터의 출력값
   - marks 파일의 READOUT 표식 뒤 첫 프레임이 결과 프레임: 하위 8비트가 E4M3/E5M2 결과
사용: python3 decode_results.py stim.txt expect.txt stim_marks.txt [bins.csv]
"""
import sys, csv

def e4m3_to_float(b):
    s, e, m = (b >> 7) & 1, (b >> 3) & 0xF, b & 7
    if e == 15 and m == 7: return float("nan")
    if e == 0: return (-1)**s * (m / 8) * 2**-6
    return (-1)**s * (1 + m / 8) * 2**(e - 7)

def e5m2_to_float(b):
    s, e, m = (b >> 7) & 1, (b >> 2) & 0x1F, b & 3
    if e == 31: return float("nan") if m else (-1)**s * float("inf")
    if e == 0: return (-1)**s * (m / 4) * 2**-14
    return (-1)**s * (1 + m / 4) * 2**(e - 15)

stim = [l.strip() for l in open(sys.argv[1]) if l.strip()]
exp = {}
for l in open(sys.argv[2]):
    p = l.split()
    if len(p) >= 2: exp[int(p[0])] = p[1]
marks = []
if len(sys.argv) > 3:
    for l in open(sys.argv[3]):
        i, _, t = l.partition(" "); marks.append((int(i), t.strip()))
bins = []
if len(sys.argv) > 4:
    for r in csv.DictReader(open(sys.argv[4])):
        bins.append((int(r["start"]), int(r["end"]), r["bin"], r["name"]))

def bin_of(i):
    for s, e, b, n in bins:
        if s <= i <= e: return f"bin{b}:{n}"
    return ""

# 프레임 추출: ssn 0 구간
frames = []; i = 0; n = len(stim)
while i < n:
    if stim[i][1] == '0':
        st = i; bits = []; prev_sclk = '0'
        while i < n and stim[i][1] == '0':
            if stim[i][2] == '1' and prev_sclk == '0':
                bits.append(exp.get(i, '?'))
            prev_sclk = stim[i][2]; i += 1
        frames.append((st, i - 1, bits))
    else:
        i += 1

mi = 0
for st, en, bits in frames:
    tags = []
    while mi < len(marks) and marks[mi][0] <= st:
        tags.append(marks[mi][1]); mi += 1
    word = "".join(bits)
    if len(bits) == 16 and all(b in "01" for b in bits):
        v = int(word, 2); lo = v & 0xFF
        note = f"= 0x{v:04x}  result8=0x{lo:02x}  E4M3={e4m3_to_float(lo):g}  E5M2={e5m2_to_float(lo):g}"
    else:
        note = f"(bits={word})"
    if tags or "READOUT" in " ".join(tags):
        print(f"[{st:7d}] {bin_of(st):28s} {' | '.join(tags):40s} MISO {note}")
