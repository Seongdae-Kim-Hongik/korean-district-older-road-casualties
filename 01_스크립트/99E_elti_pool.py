#!/usr/bin/env python3
# ELTI(2026-11-19) — 공변량 풀: INPT 정본 풀(EXT_canonical_pool_INPT_261115.csv, 2011-2024, 강제통제·수급률 정정본·교통문화지수) + 도로안전 변수 KOSIS 원표 재수집(분자·분모 합으로 비율 재계산):
#  cars_per_capita = 자동차등록대수/주민등록인구(DT_1YL20731), drink_drive_crash_share = 음주운전 사고/전체 사고×100(DT_1YL14001), all_crash_per1000 = 전체 교통사고/인구×1000(DT_1YL13901 B, 발생지 노출 대리·민감도 전용)
#  drink_driving_rate = KCHS 운전자 연간 음주운전 경험률 SR(기준 SQLite, 2026-11-19 추가).
#  seatbelt_rate = KCHS 운전자석 안전벨트 착용률 SR(기준 SQLite). 결측: 시군구 내 선형 보간 → 가장 가까운 해 이월(규칙표 기록). 산출: 02_패널/EXT_canonical_pool_ELTI_261119.csv, 04_분석/ELTI/gate/pool_fill_log.csv
import os, sys, sqlite3, unicodedata
import numpy as np, pandas as pd
sys.argv = [sys.argv[0]]; R = os.environ.get("ST_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
exec(open(f"{R}/01_스크립트/99E_elti_build.py").read().split("A = load(")[0])   # load·to_sgg·S·CD2R·EXPL 재사용
NFC = lambda s: unicodedata.normalize("NFC", str(s))
P = pd.read_csv(f"{R}/02_패널/EXT_canonical_pool_INPT_261115.csv"); P["fbd_region"] = P.fbd_region.map(NFC); P = P.drop(columns=["inpt_days"])
def tab(T, item):
    C, nat, sid = to_sgg(load(T), item, T); return C
V = pd.DataFrame({"cars": tab("DT_1YL20731", "자동차등록대수＜br＞(A)"), "res": tab("DT_1YL20731", "주민등록인구＜br＞(B)"),
                  "dd": tab("DT_1YL14001", "음주운전 교통사고발생건수＜br＞(A)"), "acc14": tab("DT_1YL14001", "교통사고 발생건수＜br＞(B)"),
                  "acc13": tab("DT_1YL13901", "전체 교통사고발생건수＜br＞(B)")}).reset_index()
V["fbd_region"] = V.sigungu_cd.map(CD2R); VALL = V.copy(); V = V[V.year.between(2011, 2024)]
V["cars_per_capita"] = V.cars / V.res; V["drink_drive_crash_share"] = V.dd / V.acc14 * 100; V["all_crash_per1000"] = V.acc13 / V.res * 1000
sb = pd.read_sql("select year, fbd_region, kchs__DT_H_BELT__SR seatbelt_rate, kchs__DT_117075_H_DR_DRIV__SR drink_driving_rate from region_year where year between 2011 and 2024", con); sb["fbd_region"] = sb.fbd_region.map(NFC)
X = P.merge(V[["year", "fbd_region", "cars_per_capita", "drink_drive_crash_share", "all_crash_per1000"]], on=["year", "fbd_region"], how="left").merge(sb, on=["year", "fbd_region"], how="left")
assert len(X) == len(P) == 229 * 14
fl = []
for c in ("cars_per_capita", "drink_drive_crash_share", "all_crash_per1000", "seatbelt_rate", "drink_driving_rate"):
    for r, g in X.groupby("fbd_region"):
        m = g[c].isna()
        if m.any(): fl.append((c, r, g.year[m].tolist(), "보간/이월"))
    X[c] = X.groupby("fbd_region")[c].transform(lambda s: s.interpolate(limit_direction="both"))
    assert X[c].notna().all(), c
pd.DataFrame(fl, columns=["var", "fbd_region", "years", "rule"]).to_csv(f"{R}/04_분석/ELTI/gate/pool_fill_log.csv", index=False, encoding="utf-8-sig")
X.to_csv(f"{R}/02_패널/EXT_canonical_pool_ELTI_261119.csv", index=False, encoding="utf-8-sig")
print(X.shape, "채움", len(fl), "건"); print(X[["cars_per_capita", "drink_drive_crash_share", "all_crash_per1000", "seatbelt_rate", "traffic_culture_index"]].describe().round(3).to_string())
print(pd.DataFrame(fl).groupby(0).size())
# ── 분모 민감도 E_crash: 그 시군구 전체 교통사고 건수(발생지) × 그해 전국 (노인 부상자 / 전체 사고) — 발생지 노출(통행·관광·통과 교통) 대리 ──
E = pd.read_csv(f"{R}/02_패널/ELTI_E69.csv", encoding="utf-8-sig"); E["fbd_region"] = E.fbd_region.map(NFC)
A13 = VALL[["year", "fbd_region", "acc13"]].copy(); A13["acc13"] = pd.to_numeric(A13.acc13)
E = E.drop(columns=[c for c in ("acc_all", "E_crash") if c in E.columns]).merge(A13.rename(columns={"acc13": "acc_all"}), on=["year", "fbd_region"], how="left")
k = E[E.year <= 2024].groupby("year").cases.sum() / E[E.year <= 2024].groupby("year").acc_all.sum(); E["E_crash"] = E.acc_all * E.year.map(k)
assert E.loc[E.year <= 2024, "E_crash"].gt(0).all(), E[E.E_crash.isna() & (E.year <= 2024)]
E.to_csv(f"{R}/02_패널/ELTI_E69.csv", index=False, encoding="utf-8-sig"); print("E_crash 추가; ρ(SMR_std, SMR_crash) =", round((E.cases / E.E_std).corr(E.cases / E.E_crash, method="spearman"), 3))
