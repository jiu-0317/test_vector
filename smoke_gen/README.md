# smoke_test T7~T9 케이스 생성/검증 도구 (mpw_test 폴더에서 실행)

- model.py            : 칩 데이터패스 비트 정확 모델 (IR/FPU/ACC_adder/ACC/ACC_R)
- gen_smoke_cases.py  : 케이스 생성 -> smoke_cases.json
                        golden(테스트 벡터 MAC 52개) + cover(내부 경로 커버) + random(40개)
                        cover/random 은 결과가 0/포화/NaN 이 아닌(오류가 보이는) 케이스만
- order_and_embed.py  : 연속 기대값이 서로 다르게 정렬 -> cases_block.txt (smoke_test.py 의 CASES 블록)
- sim_cases.py        : 케이스를 iverilog 로 RTL / GLS(TOP_new.v) 시뮬해 모델 기대값과 비교

검증 결과 (2026-10-16)
- 모델 vs 기존 GLS 골든 READOUT 58개: 전부 일치
- 모델 vs RTL: smoke 케이스 + 넓은 범위 랜덤 3,000개 전부 일치
- 최종 smoke 109케이스: RTL, GLS 모두 일치 (x 0)

사용 (mpw_test 폴더, iverilog 필요):
  cp smoke_gen/*.py .
  python3 gen_smoke_cases.py && python3 order_and_embed.py
  python3 sim_cases.py smoke_cases.json 0 rtl gls
