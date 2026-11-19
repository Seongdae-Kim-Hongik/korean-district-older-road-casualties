#!/usr/bin/env python3
# ELTI(2026-11-19) — KOSIS e-지방지표 원표 재수집 2011-2025: DT_1YL202108(노인 교통사고, 경찰청, 발생지) · DT_1YL20631(고령인구비율, 주민등록 65+)
#  키: ~/.kosis_key(내용 출력 금지). 산출: 04_분석/ELTI/src/<TBL>_<연도>.json
import os, json, time, urllib.request, urllib.parse
KEY = open(os.path.expanduser("~/.kosis_key")).read().strip()
OUT = os.path.join(os.environ.get("ST_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "04_분석", "ELTI", "src"); os.makedirs(OUT, exist_ok=True)
import sys
for T in (sys.argv[1:] or ["DT_1YL202108", "DT_1YL20631"]):
    for y in range(2011, 2026):
        f = os.path.join(OUT, f"{T}_{y}.json")
        if os.path.exists(f) and os.path.getsize(f) > 1000: continue
        q = dict(method="getList", apiKey=KEY, itmId="ALL", objL1="ALL", format="json", jsonVD="Y", prdSe="Y", startPrdDe=str(y), endPrdDe=str(y), orgId="101", tblId=T)
        url = "https://kosis.kr/openapi/Param/statisticsParameterData.do?" + urllib.parse.urlencode(q)
        for k in range(4):
            try:
                d = json.loads(urllib.request.urlopen(url, timeout=60).read().decode("utf-8")); break
            except Exception as e:
                print("retry", T, y, type(e).__name__); time.sleep(5)
        if isinstance(d, dict): print("ERR", T, y, str(d)[:200]); continue
        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False); print(T, y, len(d), "rows"); time.sleep(0.5)
