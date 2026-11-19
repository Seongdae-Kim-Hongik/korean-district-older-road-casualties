#!/usr/bin/env python3
# ELTI(2026-11-19) — 노인(65+) 교통사고 부상자(경찰청 집계, 사고 발생지 시군구) 2011-2025 패널 + 분모(주민등록 65+ 인구, DT_1YL20631) + 게이트.
#  입력: 04_분석/ELTI/src/DT_1YL202108_<y>.json·DT_1YL20631_<y>.json(99E_elti_fetch.py), 기준 = 분석용 고정 복사본 SQLite(mode=ro) disease_panel(229 격자)·region_year(대조)
#  결합: 99R_next5e_injury_E.py 규칙(C1 5자리, 광주·전남 앞 '12' 제거, 세종 '29'·연기군 34320 → 29010, 일반구 → 상위 시 합(상위 시 행 버림), 명시 이관 EXPL). 원표 행 없음 = 0건(시도 합 검산).
#  E = 65+ 인구 × 그해 전국 율(65+ 내부 연령 구성은 강제통제 80+ 비율로).  산출: 02_패널/ELTI_E69.csv, 04_분석/ELTI/gate/*
import os, json, sqlite3, unicodedata, glob
import numpy as np, pandas as pd
R = os.environ.get("ST_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); SRC = f"{R}/04_분석/ELTI/src"; G = f"{R}/04_분석/ELTI/gate"; os.makedirs(G, exist_ok=True)
DB = os.path.expandvars("$ST_GPT_DATASET") + "/02_체육건강_시공간_GPT버전/02_체육건강_시공간_GPT버전.sqlite"
NFC = lambda s: unicodedata.normalize("NFC", str(s))
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
base = pd.read_sql("select distinct fbd_region, sigungu_cd from disease_panel where tag='PERIO'", con); base["fbd_region"] = base.fbd_region.map(NFC); base["sigungu_cd"] = base.sigungu_cd.astype(str)
assert len(base) == 229 and base.sigungu_cd.nunique() == 229; S = set(base.sigungu_cd); CD2R = dict(zip(base.sigungu_cd, base.fbd_region))
EXPL = {"29": "29010", "34320": "29010", "22520": "37310", "23090": "23030", "31320": "31280", "33040": "33010", "33310": "33010", "34390": "34080"}
def load(T):
    L = pd.concat([pd.DataFrame(json.load(open(f, encoding="utf-8"))) for f in sorted(glob.glob(f"{SRC}/{T}_*.json"))])
    L["DT"] = pd.to_numeric(L.DT, errors="coerce"); L["year"] = L.PRD_DE.astype(int)
    pre = L.C1.str.len().isin([4, 7]) & L.C1.str.startswith("12"); L.loc[pre, "C1"] = L.loc[pre, "C1"].str[2:]
    return L
cx = []
def to_sgg(L, item, T):
    L = L[(L.ITM_NM == item) & L.DT.notna()]; rows = []
    for y, d in L.groupby("year"):
        have = set(d.C1); kidpar = {c[:4] + "0" for c in have if len(c) == 5 and c not in S and c not in EXPL and c[:4] + "0" in S}
        for c1, nm, v in d[["C1", "C1_NM", "DT"]].itertuples(index=False):
            if c1 in EXPL: tgt, how = EXPL[c1], "명시 이관"
            elif c1 in kidpar: cx.append((T, y, c1, nm, c1, "상위 시 행(구 합 사용 → 버림)")); continue
            elif c1 in S: tgt, how = c1, "직접"
            elif len(c1) == 5 and c1[:4] + "0" in S: tgt, how = c1[:4] + "0", "일반구 합산"
            else:
                assert len(c1) <= 2, (T, y, c1, nm); continue
            if c1 == "29" and (y, "29010") in {(r[0], r[1]) for r in rows}: continue   # 세종 시군구 행이 있는 해는 머리행 무시
            rows.append((y, tgt, v)); cx.append((T, y, c1, nm, tgt, how))
    C = pd.DataFrame(rows, columns=["year", "sigungu_cd", "v"]).groupby(["year", "sigungu_cd"]).v.sum()
    nat = L[L.C1 == "00"].set_index("year").DT; sid = L[(L.C1.str.len() == 2) & (L.C1 != "00")].groupby("year").DT.sum()
    return C, nat, sid
A = load("DT_1YL202108"); P = load("DT_1YL20631")
out = pd.MultiIndex.from_product([range(2011, 2026), sorted(S)], names=["year", "sigungu_cd"]).to_frame(index=False)
log = []
for item, col in (("부상자수", "cases"), ("사고건수", "accidents"), ("사망자수", "deaths")):
    C, nat, sid = to_sgg(A, item, "DT_1YL202108"); out = out.merge(C.rename(col).reset_index(), how="left")
    s = out.groupby("year")[col].sum()
    log.append(f"{item}: 시군구 합/전국 " + str((s / nat).round(4).to_dict()) + f" | 시도 합−전국 {(sid - nat).to_dict()} | 행 없음 칸 {int(out[col].isna().sum())}")
C, nat, sid = to_sgg(P, "65세이상인구＜br＞(A)", "DT_1YL20631"); out = out.merge(C.rename("pop65").reset_index(), how="left")
log.append("65+ 인구: 시군구 합/전국 " + str((out.groupby('year').pop65.sum() / nat).round(5).to_dict()) + f" | 결측 {int(out.pop65.isna().sum())}")
C, nat, sid = to_sgg(P, "전체인구＜br＞(B)", "DT_1YL20631"); out = out.merge(C.rename("pop_all").reset_index(), how="left")
miss_rows = out[out.cases.isna()][["year", "sigungu_cd"]]; log.append("부상자 원표 행 없음 → 0건: " + str([(int(a), CD2R[b]) for a, b in miss_rows.values]))
for c in ("cases", "accidents", "deaths"): out[c] = out[c].fillna(0)
assert out.pop65.notna().all() and (out.pop65 > 0).all()
out["fbd_region"] = out.sigungu_cd.map(CD2R)
rate = out.groupby("year").cases.sum() / out.groupby("year").pop65.sum()
out["E_std"] = out.pop65 * out.year.map(rate); out["offset"] = out.pop65
popr = pd.read_sql("select year, fbd_region, population from region_year", con); popr["fbd_region"] = popr.fbd_region.map(NFC)
out = out.merge(popr, on=["year", "fbd_region"], how="left"); out["E_crude"] = out.population * out.year.map(out.groupby("year").cases.sum() / out.groupby("year").population.sum())
# 기준 SQLite 대조(세종 외)
R2 = pd.read_sql('select year, fbd_region, eloc__DT_1YL202108__부상자수 v, "eloc__DT_1YL20631__65세이상인구＜br＞(A)" p from region_year', con); R2["fbd_region"] = R2.fbd_region.map(NFC)
J = out.merge(R2, on=["year", "fbd_region"]); ok = J.v.notna(); okp = J.p.notna()
log.append(f"기준 SQLite 대조 부상자수 일치 {int((J.v[ok] == J.cases[ok]).sum())}/{int(ok.sum())}, 65+ 인구 일치 {int((J.p[okp] == J.pop65[okp]).sum())}/{int(okp.sum())}; 불일치 예 " + str(J[ok & (J.v != J.cases)][["year", "fbd_region", "v", "cases"]].head(8).values.tolist()))
log.append(f"세종 연도별 부상자 {out[out.sigungu_cd=='29010'].set_index('year').cases.astype(int).to_dict()} 65+ {out[out.sigungu_cd=='29010'].set_index('year').pop65.astype(int).to_dict()}")
yt = out.groupby("year").agg(cases=("cases", "sum"), pop65=("pop65", "sum"), accidents=("accidents", "sum"), deaths=("deaths", "sum")); yt["rate_per100k"] = yt.cases / yt.pop65 * 1e5
yt.to_csv(f"{G}/national_by_year.csv", encoding="utf-8-sig"); log.append("전국 연도별:\n" + yt.round(1).to_string())
q = out.assign(r=out.cases / out.pop65 * 1e5).groupby("year").r.describe(percentiles=[.1, .5, .9]); log.append("시군구 율(10만 65+) 분포:\n" + q.round(1).to_string())
out["ratio_inj_per_acc"] = out.cases / out.accidents.replace(0, np.nan)
assert not out.duplicated(["year", "fbd_region"]).any() and out.groupby("year").fbd_region.nunique().min() == 229 and (out.E_std > 0).all()
out[["year", "fbd_region", "sigungu_cd", "offset", "cases", "E_std", "E_crude", "pop65", "pop_all", "accidents", "deaths"]].to_csv(f"{R}/02_패널/ELTI_E69.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(cx, columns=["표", "year", "C1", "C1_NM", "sigungu_cd", "처리"]).to_csv(f"{G}/C1_crosswalk.csv", index=False, encoding="utf-8-sig")
open(f"{G}/gate_build_log.txt", "w").write("\n".join(log)); print("\n".join(log))
