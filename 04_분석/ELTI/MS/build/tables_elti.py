# tables_elti.py — ELTI 본문 표 2개(수치는 numbers_elti에서만). the journal: 표는 관련 본문 옆, 제목·설명 위, 각주 아래, 숫자 3자리 이내 반올림.
from docx.shared import Pt
from numbers_elti import HYP, FORCED, CAR, PAVE, TCI, BELT, DRK, BLS, TE, P80
WC = ["W1_2011-15", "W2_2016-19", "W3_2020-24", "ALL"]; WH = ["2011–2015", "2016–2019", "2020–2024", "2011–2024"]
COVLAB = [(CAR, "Registered motor vehicles per resident, natural log"), (PAVE, "Paved share of roads, %"), (TCI, "Traffic culture index, points"), (BELT, "Driver seat-belt wearing, %"), (DRK, "Drink-driving among drivers, %"),
          (BLS, "Basic livelihood recipients, %"), (TE, "Tertiary-educated adults, %"), (P80, "Population aged ≥ 80 years, %")]
LABEL = {CAR: "Motor vehicles per resident (+)", PAVE: "Paved share of roads (±)", TCI: "Traffic culture index (−)", BELT: "Driver seat-belt wearing (−)", DRK: "Drink-driving among drivers (+)",
         BLS: "Basic livelihood recipients (+)", TE: "Tertiary-educated adults (−)", "urban_population_share": "Urban population share", "physicians_per_1000": "Physicians per 1,000",
         "sex_ratio": "Sex ratio", "fiscal_independence": "Fiscal autonomy", "pop80_share": "Population aged ≥ 80 years"}
GROUPS = [("Vehicle exposure and road environment", [CAR, PAVE]), ("Road-user behaviour", [TCI, BELT, DRK]), ("Socioeconomic conditions", [BLS, TE]), ("Forced controls", FORCED)]

def table1(N):
    T = N["T1"]; nat = N["nat"]
    def rate(a, b): q = nat.loc[a:b]; return q.injured.sum() / q.pop65.sum() * 1e5
    rows = [["__H__", "Injured older people"], ["  District-years, no."] + [f"{T[c]['n']:,}" for c in WC], ["  Injured people aged ≥ 65 years, no."] + [f"{T[c]['cases']:,}" for c in WC],
            ["  Rate per 100,000 aged ≥ 65 years*"] + [f"{rate(a, b):.0f}" for a, b in ((2011, 2015), (2016, 2019), (2020, 2024), (2011, 2024))],
            ["  District SIR, median (P10–P90)†"] + [f"{T[c]['med']:.2f} ({T[c]['p10']:.2f}–{T[c]['p90']:.2f})" for c in WC], ["__H__", "District characteristics, mean (SD)"]]
    for v, lab in COVLAB:
        mx = max(abs(T[c]['cov'][v][0]) for c in WC); dp = 0 if mx >= 100 else (2 if mx < 1 else 1)
        rows.append([f"  {lab}"] + [f"{T[c]['cov'][v][0]:.{dp}f} ({T[c]['cov'][v][1]:.{dp}f})" for c in WC])
    foot = ("P10–P90, 10th–90th percentile; SD, standard deviation; SIR, standardised incidence ratio. *Average annual rate: injured people summed over the period divided by residents aged 65 years or older summed over the years of the period. "
            "†Observed over expected (residents aged 65 years or older times the national rate of the year) summed over the period. Characteristics are district-year means; sources are in Table A1.")
    return (f"Table 1. Injured older road users and district characteristics, {N['n_districts']} districts, Republic of Korea, 2011–2024", ["Characteristic"] + WH, rows, foot)

def f3(t): return f"{t[0]:.3f} ({t[1]:.3f}–{t[2]:.3f})"
def table2(N, best_kh):
    rows = []
    for g, vs in GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            m = N["main"][v]; mv = N["mv"].get(v); k = N["s43"][(best_kh, v)]; c = N["s10"].set_index("cov").loc[v]; sc = N["sens"]["sc"].get(v)
            rows.append([f"  {LABEL[v]}", f3((m["IRR"], m["lo"], m["hi"])), f"{100*mv['cred_frac']:.0f}" if mv else "Forced", f3(k), f3((c.IRR, c.lo, c.hi)), f3(sc) if sc else "—"])
    kh = {"KH_typeI": "I", "KH_typeII": "II", "KH_typeIII": "III", "KH_typeIV": "IV"}[best_kh]
    foot = (f"CrI, credible interval; RR, rate ratio per 1 standard deviation; expected direction in parentheses. Principal model: negative binomial with a Besag–York–Mollié 2 district effect, random-walk and independent year effects, seven characteristics and five forced controls (n = {N['n_rows']:,} district-years). "
            f"*Share of the {N['mv_total']} covariate-subset models containing the characteristic in which the CrI excluded 1. †Knorr-Held type {kh} space-time interaction added, the best-fitting interaction model by WAIC. "
            "‡Expected counts from all police-reported crashes in the district times the national number of injured older people per crash (RR of injured older people per crash). §Expected counts from the total population times the national rate per resident.")
    return (f"Table 2. District characteristics and injured older road users, {N['n_districts']} districts, Republic of Korea, 2011–2024",
            ["Characteristic", "Principal RR (95% CrI)", "Subsets credible, %*", f"Type {kh} RR (95% CrI)†", "Per-crash expected RR (95% CrI)‡", "Total-population expected RR (95% CrI)§"], rows, foot)

def foot_row(J, text, sz=8, ls=11):
    from docx.enum.text import WD_LINE_SPACING
    t = J.doc.tables[-1]; r = t.add_row(); m = r.cells[0].merge(r.cells[-1]); m.text = ""; p = m.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(ls); p.paragraph_format.space_before = Pt(4)
    c = J.counting; J.counting = False; J._emit(p, text, sz); J.counting = c
def put_table(J, t, fs=9):
    c = J.counting; J.counting = False; J.table_fit(t[0], t[1], t[2], "", fs_max=fs, title_bold=True); foot_row(J, t[3]); J.counting = c

FIGCAP = {
 1: "Injured older road users in the Republic of Korea, 2011–2025. (a) Injured people aged 65 years or older in police-reported road traffic crashes per year (2025, red, was not used in the models). (b) Rate per 100,000 residents aged 65 years or older. (c) Injured older people per 100 police-reported crashes of any kind. The shaded band marks 2020.",
 2: "District geography of injured older road users, 229 districts, Republic of Korea, 2011–2024. (a) Standardised incidence ratio per older resident (observed over residents aged 65 years or older times the national rate). (b) Ratio per crash (observed over all police-reported crashes in the district times the national number of injured older people per crash). (c) Residual hot spots and cold spots from the principal model (posterior probability of a residual spatial rate ratio above 1 > 0.95 or < 0.05). Thick lines are province boundaries.",
 3: "Rate ratios per 1 standard deviation with 95% credible intervals for the three characteristics associated with injured older road users across models, 229 districts, Republic of Korea, 2011–2024: principal model, Knorr-Held type II (best-fitting) and type III space-time models, Spatial+-type adjustment, exclusion of the 23 districts with the highest crash rates, adjustment for the all-crash rate, and expected counts from all crashes. The horizontal axis is on a log scale."}
def place(J, what, N):
    import content_elti as C
    if what == "T1": put_table(J, table1(N))
    elif what == "T2": J.new_page("landscape"); put_table(J, table2(N, C.BEST_KH), fs=9); J.new_page("portrait")
    elif what.startswith("F"):
        import os
        k = int(what[1:]); p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs", f"ELTI_Fig{k}.png")
        from docx.shared import Mm
        c = J.counting; J.counting = False; J.doc.add_picture(p, width=Mm(160))
        J.para(f"<b>Fig. {k}.</b> {FIGCAP[k]}", before=2, after=8); J.counting = c
