# MyChip_FP_MAC MPW 테스트 벡터 흐름 (Cadence 없이, Icarus Verilog + Python)

```
mpw_test/
├─ netlist/TOP_new.v      Innovus post-layout 넷리스트 (6/8 버전 = 실제 칩, golden)
├─ lib/scl.v              Liberate 셀 라이브러리 Verilog 모델 (원본)
├─ lib/scl_sim.v          prep_lib.py 가 만든 시뮬용 (specify 제거, delayed_* 치환)
├─ lib/prep_lib.py
├─ rtl/*.v                테이프아웃 RTL (= src 폴더, ReLU + o_cmd_done 포함). TOP_new.v 와 사이클 단위 일치
├─ vec/gen_vectors.py     벡터 생성기 (bin 단위)  -> stim.txt, stim_bins.csv, stim_marks.txt
├─ vec/decode_results.py  프레임별 MISO 워드 복원 + E4M3/E5M2 값 해석
├─ vec/pack_for_fpga.py   stim+expect -> 1바이트/벡터 (vectors.bin / vectors.hex)
├─ vec/compare_log.py     FPGA 실측 로그 vs 기대값 -> bin별 PASS/FAIL (yield CSV 한 줄)
├─ sim/tb_vec.v           벡터 재생 테스트벤치 (넷리스트/RTL 공용, expect + trace + VCD 출력)
├─ sim/toggle_cov.py      VCD 토글 커버리지 (IMC 대체)
├─ run_all.sh             전체 흐름 한 번에
└─ out/                   expect_gls.txt(golden), expect_rtl.txt, trace_*.txt, toggle_report.txt,
                          results_decoded.txt, vectors.bin/hex
```

## 실행
```
sudo apt install iverilog       # (Windows: WSL 또는 iverilog 배포판, 또는 Docker)
./run_all.sh                     # 약 15초
```
순서: 벡터 생성 -> RTL 시뮬 -> GLS(TOP_new.v) 시뮬 -> RTL/GLS 비교(MATCH/MISMATCH 출력)
-> 토글 커버리지 -> 결과 해석 -> FPGA 패킹. golden 은 항상 `out/expect_gls.txt`.

## 벡터 / 기대값 정의
- stim 1줄 = `i_clk` 1사이클, `rstn ssn sclk mosi` 4비트.
- 입력은 `i_clk` 하강 직후 인가, 출력은 다음 하강 직전에 샘플 -> 그 값이 해당 벡터의 기대값.
- expect 1줄 = `<idx> <miso> <cmd_done>` (값을 정할 수 없으면 `x` = don't-care).
- FPGA 1바이트 형식:
  `bit7 MISO mask · bit6 기대 MISO · bit5 cmd_done mask · bit4 기대 cmd_done · bit3..0 {rstn,ssn,sclk,mosi}`
- FPGA 실측 로그도 expect 와 같은 `<idx> <miso> <cmd_done>` 형식으로 찍으면 compare_log.py 에 바로 넣을 수 있다.
- 파라미터: K = SCLK 반주기(`i_clk` 사이클), G = 프레임 간 SSN high 사이클. 기본 K=4, G=8.
  (bin 13 은 K=2,G=3 최소 타이밍, bin 14 는 K=16,G=32.)

## bin 목록 (stim_bins.csv)
0 reset_idle · 1 spi_loopback_zero · 2 read_without_acc · 3 all_ones_9 · 4 single_element_k(k=0..8)
· 5 overwrite_and_rerun · 6 double_read · 7 sign_relu_cancel · 8 special_values · 9 rounding
· 10 exp_diff_large · 11 modes(4조합+E5M2 특수값) · 12 random_mac(20세트) · 13 min_timing
· 14 slow_timing · 15 ignored_cmds_mosi_high · 16 negative_inputs_all_pos
각 bin 은 리셋으로 시작하므로 독립 실행/독립 판정 가능.

## 현재 결과 (TOP_new.v 기준)
- 183,877 벡터, GLS 에서 MISO / o_cmd_done 모두 X 0 사이클.
- RTL(rtl/) vs GLS: MISO, o_cmd_done 모두 완전 일치 (MATCH).
- ReLU 동작: 음수 합 -> 0x00 (bin 7).
- 토글 커버리지 97.8% (1352/1383 넷). 미달 31개:
  VDD/VSS, 미사용 r_dat[15:7]·TBUF[15]·next_state[0] (TX 상위 바이트는 항상 0),
  acc_r_data[7] (ReLU 뒤 결과 부호는 구조상 항상 0 — NaN 도 부호 0), 나머지 n_* 는 ACC_adder 극단 조건.

## 넷리스트 관련 참고
1. TOP 포트: `i_clk i_rstn i_ssn i_mosi i_sclk o_miso o_cmd_done VDD VSS`.
2. `W_I_RF` 의 `always @(i_clk)` 는 LATCHX1 래치로 합성됐다. 리셋 없음 -> 모든 MAC 테스트는 W/I 18개를 먼저 채운다.
3. Genus 가 클럭 게이팅(래치+AND) 셀을 넣었다. 기능은 동일.
4. Innovus 가 추가한 FE_*/CTS_* 버퍼에는 VDD/VSS 핀 연결이 없다 -> 시뮬 시 `-Dno_power_gate` 필수
   (없으면 전 출력 X).
5. 이전 넷리스트(TOP_net.v, 6/5~7)에는 ReLU 와 o_cmd_done 이 없었다. 더 이상 사용하지 않는다.

## FPGA 쪽 (구현 가이드)
- vectors.bin 을 BRAM 에 올리고, 벡터마다: 스캔체인에 4비트 시프트-인 -> update -> `i_clk` 1펄스 ->
  MISO / o_cmd_done 캡처 -> mask 가 1인 비트만 기대값과 비교.
  `i_clk` 과 `i_rstn` 은 스캔체인이 아니라 FPGA 핀에서 직접 주는 것을 권장.
- functional 모드: 첫 불일치에서 정지, `idx, expected, actual` 을 UART 로 출력.
- yield 모드: 전 벡터 실행하며 `idx miso cmd_done` 을 그대로 UART 로 흘려보내면 compare_log.py 가 bin 별 판정.
  bin 경계(stim_bins.csv)에서 클럭을 멈추고 IDDQ 를 재도 됨 (전부 정적 논리).
