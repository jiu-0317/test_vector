#!/bin/bash
# 전체 흐름: 벡터 생성 -> RTL 시뮬 -> GLS(TOP_new.v) 시뮬 = golden -> RTL/GLS 비교
#           -> 토글 커버리지 -> 결과 해석 -> FPGA용 패킹
# expect 파일 형식: "<idx> <miso> <cmd_done>"
# golden 은 expect_gls.txt (게이트 넷리스트). expect_rtl.txt 는 비교용.
set -e
cd "$(dirname "$0")"

# python3 가 Windows Store 스텁인 환경이 있어 실제 인터프리터를 고른다
PY=${PY:-$(command -v python3 || true)}
if [ -z "$PY" ] || ! "$PY" -c "" 2>/dev/null; then PY=$(command -v python || command -v py); fi

NETLIST=../netlist/TOP_new.v

"$PY" lib/prep_lib.py lib/scl.v lib/scl_sim.v
"$PY" vec/gen_vectors.py -o vec/stim.txt --nrand ${NRAND:-20}

cd sim
#################
#      RTL      #
#################
iverilog -g2012 -DRTL -o rtl.vvp tb_vec.v ../rtl/*.v 2> compile_rtl.log
vvp rtl.vvp +stim=../vec/stim.txt +expect=../out/expect_rtl.txt +trace=../out/trace_rtl.txt

#################
#      GLS      #
#################
# -Dno_power_gate: Innovus 가 넣은 FE_*/CTS_* 버퍼에 VDD/VSS 가 연결돼 있지 않아 필요 (없으면 전 출력 X)
iverilog -g2012 -Dno_power_gate -DVCD -o gls.vvp tb_vec.v $NETLIST ../lib/scl_sim.v 2> compile.log
vvp gls.vvp +stim=../vec/stim.txt +expect=../out/expect_gls.txt +trace=../out/trace_gls.txt
# 토글 커버리지 (넷리스트 전용, -DVCD 로 만든 dump.vcd 필요)
"$PY" toggle_cov.py dump.vcd $NETLIST ../out/toggle_report.txt
cd ..

# X 검사 (golden 에 x 가 있으면 FPGA 에서 그 사이클은 비교 안 함 -> 원인 확인 필요)
NX=$(awk '$2=="x"||$3=="x"' out/expect_gls.txt | wc -l)
echo "GLS x cycles: $NX"

# RTL vs GLS 비교
# --strip-trailing-cr: Windows vvp 는 CRLF, Linux vvp 는 LF 로 써서 줄끝이 달라진다
if diff -q --strip-trailing-cr out/expect_gls.txt out/expect_rtl.txt > /dev/null; then
    echo "MATCH: expect_rtl.txt == expect_gls.txt"
else
    echo "MISMATCH: $(diff --strip-trailing-cr out/expect_gls.txt out/expect_rtl.txt | grep -c '^<') lines (diff --strip-trailing-cr out/expect_gls.txt out/expect_rtl.txt)"
fi

# 결과 해석과 FPGA 패킹은 golden(GLS) 기준
"$PY" vec/decode_results.py vec/stim.txt out/expect_gls.txt vec/stim_marks.txt vec/stim_bins.csv > out/results_decoded.txt
"$PY" vec/pack_for_fpga.py vec/stim.txt out/expect_gls.txt out/vectors.bin out/vectors.hex
echo "done. see out/"
