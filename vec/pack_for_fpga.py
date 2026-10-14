#!/usr/bin/env python3
"""stim.txt + expect.txt -> FPGA용 1바이트/벡터 이진 파일 (+ 16진 텍스트, Verilog $readmemh용)
 byte 형식:
   bit7 = MISO mask     (1이면 MISO 비교)
   bit6 = 기대 MISO
   bit5 = cmd_done mask (1이면 o_cmd_done 비교)
   bit4 = 기대 o_cmd_done
   bit3..0 = {rstn, ssn, sclk, mosi}
 expect.txt 한 줄: "<idx> <miso> <cmd_done>"  ('x' 면 해당 mask=0)
사용: python3 pack_for_fpga.py stim.txt expect.txt vectors.bin vectors.hex
"""
import sys
stim = [l.strip() for l in open(sys.argv[1]) if l.strip()]
exp = [l.split() for l in open(sys.argv[2]) if l.strip()]
assert len(stim) == len(exp), (len(stim), len(exp))
out = bytearray()
for s, e in zip(stim, exp):
    b = int(s, 2) & 0xF
    miso, done = e[1], e[2]
    if miso in "01":
        b |= 0x80 | (int(miso) << 6)
    if done in "01":
        b |= 0x20 | (int(done) << 4)
    out.append(b)
open(sys.argv[3], "wb").write(out)
with open(sys.argv[4], "w") as f:
    for b in out: f.write(f"{b:02x}\n")
print(f"{len(out)} vectors -> {sys.argv[3]} ({len(out)} bytes), {sys.argv[4]}")
