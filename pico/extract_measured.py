#!/usr/bin/env python3
"""mpremote 출력(run_*.log)에서 "M <idx> <miso> <done>" 줄만 뽑아 measured.txt 로 저장.
 PowerShell 의 '>' 가 UTF-16 으로 저장하는 경우도 처리한다.
사용: python pico/extract_measured.py run_chip01.log measured_chip01.txt
 이후: python vec/compare_log.py out/expect_gls.txt measured_chip01.txt vec/stim_bins.csv chip01 >> yield.csv
       python vec/decode_results.py vec/stim.txt measured_chip01.txt vec/stim_marks.txt vec/stim_bins.csv
"""
import sys
raw = open(sys.argv[1], "rb").read()
if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
    txt = raw.decode("utf-16")
else:
    txt = raw.decode("utf-8", errors="replace")
n = 0
with open(sys.argv[2], "w", newline="\n") as f:
    for line in txt.splitlines():
        t = line.split()
        if len(t) == 4 and t[0] == "M":
            f.write("%s %s %s\n" % (t[1], t[2], t[3]))
            n += 1
print(f"{n} measured vectors -> {sys.argv[2]}")
