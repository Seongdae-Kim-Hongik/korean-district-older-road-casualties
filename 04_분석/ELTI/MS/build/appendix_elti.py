# appendix_elti.py — ELTI Appendix A(Supplementary material). 수치는 numbers_elti에서만. 익명(저자 정보 없음).
#  Table A1 변수 출처·단위·연도·예상 방향 · Table A2 우도 5종 · Table A3 대안 사양별 RR(가설 7) · Table A4 잔차 핫·콜드스팟 목록
import os, json, re, subprocess, unicodedata
import pandas as pd
from jkms_engine import JKMS
import content_elti as C
from tables_elti import put_table, LABEL, GROUPS
N = C.N; HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "out")
NFC = lambda s: unicodedata.normalize("NFC", str(s))
ROM = json.load(open(os.path.join(HERE, "district_romanization.json"), encoding="utf-8")) if os.path.exists(os.path.join(HERE, "district_romanization.json")) else {}

A1 = [("Injured people aged ≥ 65 years (outcome)", "National Police Agency, local indicators DT_1YL202108", "Persons, district of crash occurrence", "2011–2025", "—"),
      ("Population aged ≥ 65 years (expected counts)", "Resident registration, DT_1YL20631", "Persons", "2011–2025", "—"),
      ("All police-reported crashes (per-crash expected counts)", "National Police Agency, DT_1YL13901", "Crashes", "2011–2025", "—"),
      ("Registered motor vehicles per resident", "Ministry of Land, Infrastructure and Transport, DT_1YL20731", "Vehicles per resident (log)", "2011–2024", "+"),
      ("Paved share of roads", "Road statistics, DT_1YL20721", "%", "2013–2024*", "±"),
      ("Traffic culture index", "Korea Transportation Safety Authority survey, DT_1YL20331", "Points (0–100)", "2011–2024*", "−"),
      ("Driver seat-belt wearing", "Community Health Survey", "Age-standardised %", "2011–2024*", "−"),
      ("Drink-driving among drivers (past year)", "Community Health Survey", "Age-standardised %†", "2011–2024*", "+"),
      ("Basic livelihood security recipients", "Ministry of Health and Welfare", "% of population (2021–2023 general-ward cities corrected)", "2011–2024", "+"),
      ("Tertiary-educated adults", "Population and Housing Census", "% of adults", "2011–2024*", "−"),
      ("Urban population share (forced)", "Ministry of Land, Infrastructure and Transport", "%", "2011–2024", "Control"),
      ("Physicians per 1,000 (forced)", "Health Insurance Review and Assessment Service", "Per 1,000", "2011–2024", "Control"),
      ("Sex ratio (forced)", "Resident registration", "Men per 100 women", "2011–2024", "Control"),
      ("Fiscal autonomy (forced)", "Ministry of the Interior and Safety", "%", "2011–2024", "Control"),
      ("Population aged ≥ 80 years (forced)", "Resident registration", "% of total population", "2011–2024", "Control"),
      ("Transport-injury deaths, all ages (comparison)", "Cause-of-death statistics, ICD-10 V01–V99", "Deaths, district of residence", "2011–2024", "—"),
      ("CPR awareness (negative control)", "Community Health Survey", "%", "2011–2024*", "None"),
      ("Fires per 10,000 (negative control)", "National Fire Agency", "Per 10,000", "2011–2024", "None"),
      ("Deaths with ill-defined causes (negative control)", "Cause-of-death statistics", "% of deaths", "2011–2024", "None")]
def tA1():
    foot = ("*Missing district-years were filled by linear interpolation within the district (nearest year at the ends); the survey and census items are interpolated between survey years. "
            "†District means fell from 6.3% in 2019 to 2.8% in 2020 and stayed near that level, which may reflect a change in the survey; national shifts are absorbed by the year effects. All characteristics were standardised to mean 0 and SD 1 over district-years before modelling. CPR, cardiopulmonary resuscitation.")
    return ("Table A1. District characteristics, sources, units, years and expected direction", ["Characteristic", "Source", "Unit", "Years", "Expected direction"], [list(r) for r in A1], foot)

def tA2():
    L = N["lik"]; NAMES = [("poisson", "Poisson"), ("nbinomial", "Negative binomial (principal)"), ("zeroinflatedpoisson1", "Zero-inflated Poisson"), ("zeroinflatednbinomial1", "Zero-inflated negative binomial"), ("poisson+obs_iid", "Poisson with observation-level effect")]
    rows = [[lab, f"{L[k]['WAIC']:,.1f}", f"{L[k]['DIC']:,.1f}", f"{L[k]['neg_logscore']:,.1f}"] for k, lab in NAMES]
    foot = (f"All models: five forced controls, Besag–York–Mollié 2 district effect, random-walk and independent year effects, offset of log expected counts; n = {N['n_rows']:,} district-years, none with zero injuries. "
            "DIC, deviance information criterion; WAIC, widely applicable information criterion; −Σlog CPO, negative sum of log conditional predictive ordinates (lower is better for all three).")
    return ("Table A2. Likelihood comparison", ["Likelihood", "WAIC", "DIC", "−Σlog CPO"], rows, foot)

SPEC = [("Principal model", lambda v: (N["main"][v]["IRR"], N["main"][v]["lo"], N["main"][v]["hi"])),
        ("Knorr-Held type I", lambda v: N["s43"][("KH_typeI", v)][:3]), ("Knorr-Held type II", lambda v: N["s43"][("KH_typeII", v)][:3]),
        ("Knorr-Held type III", lambda v: N["s43"][("KH_typeIII", v)][:3]), ("Knorr-Held type IV", lambda v: N["s43"][("KH_typeIV", v)][:3]),
        ("Poisson with observation-level effect", lambda v: N["s41"][("C1_poisson_lognormal", v)][:3]), ("Second-order random walk for year", lambda v: N["s41"][("C2_rw2_year", v)][:3]),
        ("Province-by-year effect", lambda v: N["s41"][("C4_sido_year_iid", v)][:3]), ("Characteristics lagged 1 year", lambda v: N["s41"][("E1_lag1", v)][:3]),
        ("Spatial+-type adjustment", lambda v: N["s41"][("D1_spatial_plus", v)][:3]), ("Restricted spatial regression", lambda v: N["s43"][("RSR", v)][:3]), ("Survey items, 3-year moving average", lambda v: N["s41"][("G1_kchs_ma3", v)][:3]),
        ("Queen contiguity graph", lambda v: N["sens"]["s577"][v][:3]), ("Without share aged ≥ 80 years", lambda v: N["sens"]["s2"].get(v, (None,))[:3] if v in N["sens"]["s2"] else None),
        ("Expected counts from total population", lambda v: N["sens"]["sc"][v][:3]), ("Expected counts from all crashes", lambda v: C.CR(v)),
        ("Crash-based expected counts plus older share", lambda v: C.CRO(v)[:3]), ("Excluding top tenth by crash rate", lambda v: C.X(C.TOP, v)[:3]), ("Adding all-crash rate", lambda v: C.X("plus_all_crash_rate", v)[:3])]
def f3(t): return "—" if t is None else f"{t[0]:.3f} ({t[1]:.3f}–{t[2]:.3f})" + ("*" if (t[1] > 1 or t[2] < 1) else "")
def tA3():
    HV = [v for g, vs in GROUPS[:-1] for v in vs]; rows = []
    for lab, f in SPEC:
        rows.append([lab] + [f3(f(v)) for v in HV])
    hdr = ["Specification"] + [LABEL[v].split(" (")[0] for v in HV]
    foot = "Rate ratios per 1 SD increase (95% credible interval); *interval excludes 1 before rounding. Knorr-Held type I, unstructured district by unstructured year; II, unstructured district by random-walk year; III, structured district by unstructured year; IV, structured by structured. Omission of each of 17 provinces and 14 years is summarised in the text."
    return ("Table A3. Rate ratios across alternative specifications", hdr, rows, foot)

def tA4():
    s6 = N["s6"].copy(); s6 = s6[s6["class"] != "neutral"].sort_values(["class", "RR"], ascending=[False, False])
    rows = [[ROM.get(NFC(r.fbd_region), NFC(r.fbd_region)), "Hot spot" if r["class"] == "hotspot" else "Cold spot", f"{r.RR:.2f} ({r.lo:.2f}–{r.hi:.2f})", f"{r.P_gt1:.3f}", f"{r.SIR_obs:.2f}"] for _, r in s6.iterrows()]
    foot = "Residual spatial rate ratio from the principal model (95% credible interval). Hot spot, posterior probability that the residual RR exceeds 1 (P(RR > 1)) above 0.95; cold spot, below 0.05 (one-sided, not adjusted for multiple comparisons; a two-sided 95% interval may include 1). SIR, observed over expected injured older people per older resident, 2011–2024."
    return ("Table A4. Residual hot spots and cold spots", ["District", "Class", "Residual RR (95% CrI)", "P(RR > 1)", "SIR"], rows, foot)

if __name__ == "__main__":
    J = C.__dict__.get("TX", None)
    from build_manuscript_elti import TX
    J = TX(cite="ay"); J.para("<b>Appendix A. Supplementary material</b>"); J.para(f"<b>{C.TITLE}</b>", before=6)
    J.head("A.1 Data processing", 2)
    J.para("Counts were rebuilt from the public KOSIS tables by administrative code. General wards (gu) of cities were summed to the city; the Sejong City row was used from 2012, Yeongi County (2011–2012) was assigned to Sejong City, Cheongwon County to Cheongju City (2011–2013), and Gunwi County, transferred to Daegu in 2023, was kept as one district throughout. The district counts of injured people, crashes and deaths and the population aged 65 years or older summed exactly to the national totals in each year from 2011 to 2025, and no district-year was missing. By construction, expected counts summed to the observed counts in each year.")
    J.head("A.2 Model and priors", 2)
    J.para("Counts were modelled as negative binomial with log link and an offset of log expected counts. Fixed effects had normal priors with mean 0 and precision 4 (intercept precision 0.001). The Besag–York–Mollié 2 district effect used the scaled 593-edge contact graph of the 229 districts (islands linked to their nearest district), a penalised-complexity prior on its precision (P(SD > 0.5) = 0.01) and on the mixing parameter φ (P(φ < 0.5) = 2/3), and a sum-to-zero constraint. Year effects were a scaled first-order random walk and an independent effect, each with the same penalised-complexity precision prior. Models were fitted with R-INLA 25.10.19 (one thread). The residual spatial RR is the exponentiated structured-plus-unstructured district effect. Residual Moran's I used row-standardised queen weights and 999 permutations.")
    J.page_break(); put_table(J, tA1(), fs=8)
    J.page_break(); put_table(J, tA2(), fs=8)
    t = tA3(); h = t[1]; r = t[2]
    J.new_page("landscape"); put_table(J, (t[0] + " (part 1)", h[:5], [x[:5] for x in r], t[3]), fs=8)
    J.page_break(); put_table(J, (t[0] + " (part 2)", [h[0]] + h[5:], [[x[0]] + x[5:] for x in r], t[3]), fs=8)
    J.new_page("portrait"); put_table(J, tA4(), fs=8)
    p = os.path.join(OUT, "Supplementary_Material_Appendix_A.docx"); J.doc_title = ""; J.save(p)
    subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_elti", "--convert-to", "pdf", "--outdir", OUT, p], check=True, capture_output=True); print("Appendix A ok")
