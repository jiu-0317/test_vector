#!/usr/bin/env python3
"""Liberate가 만든 셀 라이브러리 Verilog를 오픈소스 시뮬레이터(Icarus)용으로 정리
 - specify~endspecify 블록 제거 (제로딜레이 기능 시뮬)
 - $setuphold 가 만드는 delayed_* 신호를 원 신호로 치환 (Icarus는 타이밍 체크 미지원)
"""
import re, sys
src, dst = sys.argv[1], sys.argv[2]
txt = open(src).read()
txt = re.sub(r"\n\s*specify.*?endspecify", "", txt, flags=re.S)          # specify 제거
txt = re.sub(r"\n\s*wire\s+delayed_[^;]*;", "", txt)                      # wire delayed_.. 선언 제거
txt = re.sub(r"\bdelayed_(\w+)", r"\1", txt)                              # delayed_X -> X
txt = re.sub(r"\n\s*reg notifier;", "\n\treg notifier = 1'b0;", txt)      # notifier 초기화 (x 방지)
open(dst, "w").write(txt)
print("written", dst)
