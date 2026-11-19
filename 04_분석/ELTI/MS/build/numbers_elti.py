# numbers_elti.py — ELTI(노인 65+ 교통사고 부상자, 발생지) 원고의 모든 수치를 결과 CSV에서 읽는다(2026-11-19, numbers_sknd.py 구조 이식). 손입력 금지, assert로 정합 확인.
import os, glob, json, numpy as np, pandas as pd
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(os.path.dirname(HERE)); RS = os.path.join(B, "results_std3"); DESC = os.path.join(B, "results_desc")
ROOT = os.path.dirname(os.path.dirname(B)); PAN = os.path.join(ROOT, "02_패널")
WIN = [("W1_2011-15", 2011, 2015), ("W2_2016-19", 2016, 2019), ("W3_2020-24", 2020, 2024)]
rd = lambda f, d=RS, **k: pd.read_csv(os.path.join(d, f), encoding="utf-8-sig", **k)
CAR, PAVE, TCI, BELT, DRK, BLS, TE = ("ext__cars_per_capita", "ext__road_pavement_rate", "traffic_culture_index", "ext__seatbelt_rate", "ext__drink_driving_rate", "basic_livelihood_rate", "tertiary_educated_share")
HYP = [CAR, PAVE, TCI, BELT, DRK, BLS, TE]
FORCED = ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"]
P80 = "pop80_share"

def load():
    N = {}
    P = pd.read_csv(os.path.join(B, "panel_ELTI_std3.csv")); N["n_rows"], N["n_districts"] = len(P), P.fbd_region.nunique(); assert (N["n_rows"], N["n_districts"]) == (3206, 229)
    N["cases_total"] = int(P.cases.sum()); assert N["cases_total"] == 531827
    N["zeros"] = int((P.cases == 0).sum()); N["min_cases"] = int(P.cases.min()); N["median_cases"] = float(P.cases.median())
    N["desc"] = json.load(open(os.path.join(DESC, "D_summary.json"))); assert N["desc"]["inj_total_1124"] == N["cases_total"]
    N["nat"] = rd("D1_national.csv", DESC).set_index("year")
    T1 = {}
    for wn, a, b in WIN + [("ALL", 2011, 2024)]:
        q = P[P.year.between(a, b)]; g = q.groupby("fbd_region")[["cases", "E"]].sum(); smr = g.cases / g.E
        T1[wn] = dict(n=len(q), cases=int(q.cases.sum()), pop65=float(q.offset.sum()), p10=smr.quantile(.1), med=smr.median(), p90=smr.quantile(.9),
                      cov={v: (q[f"{v}_raw"].mean(), q[f"{v}_raw"].std()) for v in HYP + FORCED if f"{v}_raw" in q})
    N["T1"] = T1
    lk = rd("S1_likelihood.csv"); lk = lk[lk.set == "REF_forced_only"].set_index("family").WAIC; N["waic_pois"], N["waic_nb"] = lk["poisson"], lk["nbinomial"]; assert N["waic_nb"] < N["waic_pois"]
    hb = open(os.path.join(B, "HM_best_ELTI_std3.txt")).read(); N["hb"] = hb
    s6m = rd("S6_moran_year.csv"); N["moran_year"] = (s6m.moran_I.min(), s6m.moran_I.max()); N["moran_year_max_y"] = int(s6m.loc[s6m.moran_I.idxmax(), "year"])
    r8 = rd("S8_residual_moran.csv").set_index("quantity"); N["moran_pooled"] = r8.loc["observed_logSIR_pooled", "moran_I"]
    N["moran_resid"], N["moran_resid_p"], N["moran_resid_exp"] = r8.loc["pearson_residual_area_mean", "moran_I"], r8.loc["pearson_residual_area_mean", "p_perm"], r8.loc["pearson_residual_area_mean", "expected_I"]
    h = rd("S3_main_hyper.csv"); ph = h[h.hyperpar.str.startswith("Phi")].iloc[0]; N["phi"] = (ph["mean"], ph["X0.025quant"], ph["X0.975quant"])
    sz = h[h.hyperpar.str.startswith("size")].iloc[0]; N["nb_size"] = (sz["mean"], sz["X0.025quant"], sz["X0.975quant"])
    s6 = rd("S6_spatial_RR.csv", dtype={"sigungu_cd": str}); N["s6"] = s6; N["rr_min"], N["rr_max"] = s6.RR.min(), s6.RR.max()
    N["n_hot"], N["n_cold"] = int((s6["class"] == "hotspot").sum()), int((s6["class"] == "coldspot").sum())
    sido = s6.fbd_region.str.extract(r"^(\S+?(?:도|시))")[0]
    N["hot_by_sido"] = s6[s6["class"] == "hotspot"].groupby(sido).size().sort_values(ascending=False).to_dict()
    N["cold_by_sido"] = s6[s6["class"] == "coldspot"].groupby(sido).size().sort_values(ascending=False).to_dict()
    N["metro_cold"] = sum(N["cold_by_sido"].get(k, 0) for k in ("서울시", "부산시", "인천시")); N["n_metro"] = int(sido.isin(["서울시", "부산시", "인천시"]).sum())
    pe = rd("S12_persistence.csv").set_index("set"); N["kendall"] = pe.kendall_W.to_dict()
    N["ehsa"] = rd("S11_ehsa_summary.csv").set_index("category").n.to_dict()
    vp = rd("S42_variance_partition.csv").set_index("component"); N["vp"] = vp.share_of_linear_predictor_var.to_dict()
    m3 = rd("S3_main_IRR.csv").set_index("cov"); N["main"] = m3[["IRR", "lo", "hi", "cred", "role"]].to_dict("index")
    N["n_hyp"] = int((m3.role == "hypothesis").sum()); assert N["n_hyp"] == 7 and set(m3.index[m3.role == "hypothesis"]) == set(HYP)
    N["cred_hyp"] = sorted(v for v in HYP if N["main"][v]["cred"])
    s7 = rd("S7_multiverse_summary.csv").set_index("cov"); N["mv"] = s7[["n_specs", "cred_frac", "sign_agree", "robust"]].to_dict("index"); N["robust"] = sorted(s7.index[s7.robust])
    N["mv_total"] = int(s7.n_specs_total.iloc[0])
    nc = rd("S3_negcontrol.csv").set_index("cov"); N["negctl"] = {v: (r.IRR, r.lo, r.hi, bool(r.cred)) for v, r in nc.iterrows()}
    wi = rd("S4_window_IRR.csv"); N["win"] = {(r.cov, r.window): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in wi.itertuples()}
    N["win_ncred"] = [sum(1 for v in HYP if N["win"].get((v, w), (0, 0, 0, False))[3]) for w, _, _ in WIN]
    S43 = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RS, "S43_part_*.csv")) if "failed" not in f]); N["s43"] = {(r.analysis, r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in S43.itertuples()}
    N["s43_waic"] = S43.groupby("analysis").WAIC.first().to_dict()
    T9 = rd("S9_typeI_IRR.csv"); N["s43"].update({("KH_typeI", r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in T9.itertuples()}); N["s43_waic"]["KH_typeI"] = float(T9.WAIC.iloc[0])
    S41 = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RS, "S41_part_*.csv"))]); N["s41"] = {(r.analysis, r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in S41.itertuples()}
    N["s41_waic"] = S41.groupby("analysis").WAIC.first().to_dict(); N["s41_names"] = sorted(S41.analysis.unique())
    ret = rd("S41_retention_by_cov.csv").set_index("cov"); N["ret"] = {v: (int(ret.loc[v, "kept"]), int(ret.loc[v, "n_specs"])) for v in ret.index}
    N["bw"] = {r.cov: (r.IRR, r.lo, r.hi, bool(r.cred)) for r in S41[S41.analysis == "bw_twoway"].itertuples()}
    lo = rd("S41_leaveout_ranges.csv"); N["leaveout"] = {(r.set, r.cov): (r.n, r.n_cred_same_sign) for r in lo.itertuples() if not str(r.cov).startswith("__")}
    N["evalue"] = rd("S41_evalues.csv").set_index("cov").to_dict("index") if os.path.exists(os.path.join(RS, "S41_evalues.csv")) else {}
    N["sens"] = {}
    for v in ("s577", "s2", "sc"):
        f = os.path.join(B, f"results_{v}", "S3_main_IRR.csv")
        if os.path.exists(f): m = pd.read_csv(f).set_index("cov"); N["sens"][v] = {c: (m.loc[c, "IRR"], m.loc[c, "lo"], m.loc[c, "hi"], bool(m.loc[c, "cred"])) for c in m.index}
    N["s10"] = rd("S10_offset_sensitivity_IRR.csv")
    x = rd("S69S_exposure_sens.csv"); N["s69s"] = {(r.analysis, r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in x.itertuples()}; N["s69s_waic"] = x.groupby("analysis").WAIC.first().to_dict()
    N["s69s_top"] = open(os.path.join(RS, "S69S_top10pct_districts.txt")).read().split()
    lk = rd("S69K_likelihood.csv").set_index("likelihood"); N["lik"] = lk.to_dict("index")
    cv = rd("S5_covid.csv"); N["covid_main"] = tuple(cv[cv.term == "post_main"][["IRR", "lo", "hi", "cred"]].iloc[0])
    N["covid_inter_cred"] = int(cv[cv.term == "var_x_post"].cred.astype(bool).sum())
    eb = rd("S12c_yearly_EB_SIR.csv"); g = eb.groupby("year").ebSIR; gap = pd.DataFrame({"p10": g.quantile(.1), "p90": g.quantile(.9)}); gap["ratio"] = gap.p90 / gap.p10; N["gap"] = gap.to_dict("index")
    return N

if __name__ == "__main__":
    N = load()
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in N.items() if not isinstance(v, (dict, list, pd.DataFrame, tuple, str))})
    for k in ("phi", "nb_size", "moran_year", "covid_main", "cred_hyp", "robust"): print(k, N[k])
    print("hot", N["hot_by_sido"]); print("cold", N["cold_by_sido"]); print("kendall", N["kendall"]); print("vp", N["vp"]); print("s41", N["s41_names"]); print("s43", N["s43_waic"])
    print("ret", N["ret"]); print("gap", {y: round(N["gap"][y]["ratio"], 2) for y in (2011, 2024)}); print("s10", N["s10"])
