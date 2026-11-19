#!/usr/bin/env python3
# ELTI 기술 통계(2026-11-19): 전국 연도 추이 2011–2025, 시군구 SMR 분포·지속, 분모 비교(E_std 대 E_crash 대 E_crude), TRANS(운수사고 사망, 거주지) SMR 상관, 사고당 노인 부상 비중.
#  산출: 04_분석/ELTI/results_desc/D1_national.csv · D2_window_smr.csv · D3_denominator_compare.csv · D4_overlap.csv · D_summary.json
import os, json, numpy as np, pandas as pd
from scipy.stats import spearmanr
R = os.environ.get("ST_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); O = f"{R}/04_분석/ELTI/results_desc"
E = pd.read_csv(f"{R}/02_패널/ELTI_E69.csv", encoding="utf-8-sig")
nat = E.groupby("year").agg(injured=("cases", "sum"), deaths=("deaths", "sum"), crashes=("accidents", "sum"), pop65=("pop65", "sum"), pop_all=("pop_all", "sum"), all_crashes=("acc_all", "sum"))
nat["rate_per100k_65"] = nat.injured / nat.pop65 * 1e5; nat["share65_pop"] = nat.pop65 / nat.pop_all * 100; nat["injured_per_crash100"] = nat.injured / nat.all_crashes * 100
nat.to_csv(f"{O}/D1_national.csv", encoding="utf-8-sig")
S = {}
S["inj_2011"], S["inj_2019"], S["inj_2020"], S["inj_2024"], S["inj_2025"] = [int(nat.injured[y]) for y in (2011, 2019, 2020, 2024, 2025)]
S["rate_2011"], S["rate_2019"], S["rate_2020"], S["rate_2024"], S["rate_2025"] = [float(nat.rate_per100k_65[y]) for y in (2011, 2019, 2020, 2024, 2025)]
S["pop65_2011"], S["pop65_2024"], S["pop65_2025"] = [float(nat.pop65[y]) for y in (2011, 2024, 2025)]
S["deaths_2011"], S["deaths_2024"] = int(nat.deaths[2011]), int(nat.deaths[2024]); S["peak_rate_year"] = int(nat.rate_per100k_65.idxmax())
S["inj_total_1124"] = int(nat.loc[2011:2024, "injured"].sum()); S["crashes_total_1124"] = int(nat.loc[2011:2024, "crashes"].sum())
S["inj_per_crash"] = float(nat.loc[2011:2024, "injured"].sum() / nat.loc[2011:2024, "crashes"].sum())
S["share_inj_of_allcrash_2011"], S["share_inj_of_allcrash_2024"] = float(nat.injured_per_crash100[2011]), float(nat.injured_per_crash100[2024])
P = E[E.year <= 2024].copy()
W = {"2011–2015": (2011, 2015), "2016–2019": (2016, 2019), "2020–2024": (2020, 2024), "2011–2024": (2011, 2024)}
rows = []; smr = {}
for w, (a, b) in W.items():
    q = P[P.year.between(a, b)].groupby("fbd_region")[["cases", "E_std", "E_crash", "E_crude"]].sum()
    for e in ("E_std", "E_crash", "E_crude"): smr[(w, e)] = q.cases / q[e]
    s = smr[(w, "E_std")]; rows.append(dict(window=w, p10=s.quantile(.1), median=s.median(), p90=s.quantile(.9), p90_p10=s.quantile(.9) / s.quantile(.1), min=s.min(), max=s.max()))
pd.DataFrame(rows).to_csv(f"{O}/D2_window_smr.csv", index=False, encoding="utf-8-sig")
rc = [spearmanr(smr[(a, "E_crash")], smr[(b, "E_crash")])[0] for i, a in enumerate(list(W)[:3]) for b in list(W)[:3][i + 1:]]; S["rho_crash_win_min"], S["rho_crash_win_max"] = float(min(rc)), float(max(rc))
ws = list(W)[:3]; rr = [spearmanr(smr[(a, "E_std")], smr[(b, "E_std")])[0] for i, a in enumerate(ws) for b in ws[i + 1:]]
S["rho_win_min"], S["rho_win_max"] = float(min(rr)), float(max(rr)); S["p90p10_all"] = float(rows[-1]["p90_p10"])
D3 = dict(rho_std_crash=spearmanr(smr[("2011–2024", "E_std")], smr[("2011–2024", "E_crash")])[0], rho_std_crude=spearmanr(smr[("2011–2024", "E_std")], smr[("2011–2024", "E_crude")])[0])
s1, s2 = smr[("2011–2024", "E_std")], smr[("2011–2024", "E_crash")]
D3["top_decile_overlap"] = int(len(set(s1.nlargest(23).index) & set(s2.nlargest(23).index)))
acc = P.groupby("fbd_region").apply(lambda d: d.acc_all.sum() / d.pop_all.sum() * 1000, include_groups=False)
D3["rho_smr_allcrash_rate"] = spearmanr(s1, acc[s1.index])[0]; D3["rho_smrcrash_allcrash_rate"] = spearmanr(s2, acc[s2.index])[0]
pd.Series(D3).to_csv(f"{O}/D3_denominator_compare.csv", encoding="utf-8-sig"); S.update({k: float(v) for k, v in D3.items()})
T = pd.read_csv(f"{R}/04_분석/TRANS/panel_TRANS_s577.csv"); tq = T.groupby("fbd_region")[["cases", "E"]].sum(); ts = tq.cases / tq.E
old = P.groupby("fbd_region").apply(lambda d: d.pop65.sum() / d.pop_all.sum(), include_groups=False)
S["rho_smr_oldshare"] = float(spearmanr(s1, old[s1.index])[0]); S["rho_crash_oldshare"] = float(spearmanr(s2, old[s2.index])[0])
S["rho_trans"] = float(spearmanr(s1, ts[s1.index])[0]); S["n_trans_deaths"] = int(T.cases.sum())
s25 = E[E.year == 2025].set_index("fbd_region"); s24 = E[E.year == 2024].set_index("fbd_region")
S["rho_2024_2025"] = float(spearmanr(s24.cases / s24.E_std, (s25.cases / s25.E_std)[s24.index])[0])
pd.DataFrame({"smr_std": s1, "smr_crash": s2, "smr_trans": ts[s1.index], "allcrash_per1000": acc[s1.index]}).to_csv(f"{O}/D4_overlap.csv", encoding="utf-8-sig")
json.dump(S, open(f"{O}/D_summary.json", "w"), ensure_ascii=False, indent=1); print(json.dumps({k: round(v, 3) if isinstance(v, float) else v for k, v in S.items()}, ensure_ascii=False))
