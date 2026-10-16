"""smoke_cases.json -> 그룹별(T7 golden/T8 cover/T9 random) 순서 정리 (연속 기대값이 서로 다르게, 첫 케이스 != 0)
   -> smoke_test.py 에 넣을 CASES 블록 텍스트 출력"""
import json, random, sys
cases = json.load(open("smoke_cases.json"))
groups = {"T7": "golden", "T8": "cover", "T9": "random"}
r = random.Random(1)
out = {}
for t, tag in groups.items():
    lst = [c for c in cases if c["tag"] == tag]
    for attempt in range(1000):
        rest = list(lst); seq = []; prev = 0
        ok = True
        while rest:
            cand = [c for c in rest if c["exp"] != prev]
            if not cand:
                ok = False; break
            # 기대값이 가장 많이 남은 것부터 (막힘 방지)
            cnt = {}
            for c in rest: cnt[c["exp"]] = cnt.get(c["exp"], 0) + 1
            m = max(cnt[c["exp"]] for c in cand)
            pick = r.choice([c for c in cand if cnt[c["exp"]] == m])
            seq.append(pick); rest.remove(pick); prev = pick["exp"]
        if ok: break
        r.shuffle(lst)
    assert ok, t
    out[t] = seq
lines = []
for t in groups:
    lines.append('    "%s": """' % t)
    for c in out[t]:
        lines.append("%s %d %d %02x" % ("".join("%02x" % v for v in c["W"] + c["I"]), c["mi"], c["mo"], c["exp"]))
    lines.append('""",')
open("cases_block.txt", "w").write("\n".join(lines) + "\n")
json.dump(out, open("smoke_cases_ordered.json", "w"))
print({t: len(v) for t, v in out.items()})
from collections import Counter
print("exp distinct:", {t: len(set(c["exp"] for c in v)) for t, v in out.items()})
