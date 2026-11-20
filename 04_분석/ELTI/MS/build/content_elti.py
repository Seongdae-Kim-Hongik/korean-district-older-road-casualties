# content_elti.py — ELTI Materials and methods·Results 문장(수치는 numbers_elti에서만). the journal(이중 익명, Elsevier Harvard 저자-연도, 사고 단어 금지).
#  단독 저자: 1인칭 금지. Results에 해석 금지. 제목에 쌍점 금지. 가설 반대 방향은 사후로 표시, 주모형 불변.
from numbers_elti import load, HYP, FORCED, P80, CAR, PAVE, TCI, BELT, DRK, BLS, TE
N = load(); D = N["desc"]; M = N["main"]; T1 = N["T1"]
def tci(t): return f"RR {t[0]:.3f}, 95% CrI {t[1]:.3f}–{t[2]:.3f}"
def ci(v): r = M[v]; return tci((r["IRR"], r["lo"], r["hi"]))
S43 = lambda a, v: N["s43"][(a, v)]
S41 = lambda a, v: N["s41"][(a, v)]
SEN = lambda s, v: N["sens"][s][v]
KH = ("KH_typeI", "KH_typeII", "KH_typeIII", "KH_typeIV"); BEST_KH = min(KH, key=lambda a: N["s43_waic"][a])
TITLE = "Per older resident or per crash? How the choice of denominator reshapes district rankings of road injury among older people in Korea"
assert ":" not in TITLE
KEYWORDS = ["Older road users", "Road traffic injury", "Exposure denominator", "Small-area analysis", "Police crash data", "Traffic safety culture", "Korea"]
SUP = {"methods": "Appendix A", "covariates": "Table A1", "lik": "Table A2", "specs": "Table A3", "hot": "Table A4"}
sup = lambda k: SUP[k]
import pandas as _pd, os as _os
LIKF = N["lik"]
MAIN_WAIC = float(_pd.read_csv(_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))), "results_std3", "S3_main_fit.csv")).WAIC.iloc[0])

METHODS = [
("Study design and data sources",
 f"This ecological study covered all {N['n_districts']} districts (urban wards, cities and counties) of the Republic of Korea, harmonised to 2024 boundaries, over 2011–2024 ({N['n_rows']:,} district-years), and is reported according to the STROBE statement [@vonelm2007strengthening]. "
 "Annual counts of crashes, deaths and injured people from police-reported road traffic crashes in which at least one person aged 65 years or older was killed or injured, by province and district of crash occurrence, were obtained from the local indicator tables of the national statistics portal, which publish National Police Agency records compiled in the police road traffic crash analysis system [@web:kosis2026elderly]. "
 "The resident population aged 65 years or older came from resident registration in the same portal. Districts were joined across sources by administrative code only; general wards were summed to their city, Yeongi County (2011–2012) was assigned to Sejong City and Cheongwon County to Cheongju City (2011–2013) (Appendix A). "
 "The district counts summed exactly to the published national totals in every year (2011–2025), and no district-year of the outcome was missing. "
 "Only published aggregate statistics were used, and no individual could be identified. IRB_SENTENCE"),
("Outcome and expected counts",
 "The outcome was the annual number of injured people aged 65 years or older in police-reported road traffic crashes, counted by the district where the crash occurred; it comprised serious injury (treatment for 3 weeks or longer), slight injury (5 days to less than 3 weeks) and minor injury reports (less than 5 days) of road users who did not die within 30 days. "
 f"The table counts older casualties by their own age, not crashes caused by older drivers: its death column matched the official national number of road traffic deaths aged 65 years or older (for example, {int(N['nat'].loc[2018, 'deaths']):,} in 2018), and there were {D['inj_per_crash']:.2f} injured older people per crash in which an older person was a casualty. "
 "Expected counts per older resident were obtained by applying the national injury rate per resident aged 65 years or older in each year to each district's population aged 65 years or older; the observed-to-expected ratio is the standardised incidence ratio (SIR), which compares districts within each year and does not standardise for age within the older population. "
 "Because the numerator is counted where crashes occur and the denominator where people live, a second, crash-based expected count was defined: the number of all police-reported crashes in the district (any age) multiplied by the national number of injured older people per police-reported crash in that year. "
 "The resulting ratio indicates whether more or fewer older people were injured than expected from the number of crashes in the district. "
 "The two ratios are arithmetically linked: injured older people per older resident equal injured older people per crash multiplied by crashes per resident and divided by the older share of residents, so correlations between them and these components are partly structural. "
 "Data for 2025 were available and are reported descriptively; models used 2011–2024 because several district characteristics were not yet published for 2025."),
("District characteristics",
 f"Seven characteristics were fixed before any model was fitted, each with an expected direction ({sup('covariates')}). "
 "Vehicle exposure and road environment were represented by registered motor vehicles per resident (natural log, expected to raise injuries) [@mansfield2018effects] and the paved share of the road network (direction not specified: more traffic and speed versus better surfaces). "
 "Road-user behaviour was represented by the traffic culture index, a composite of observed driving behaviour, pedestrian behaviour and traffic safety conditions surveyed annually in every district (expected to lower injuries) [@benzaman2022influence], and by age-standardised driver seat-belt wearing (expected to lower injuries among occupants) [@hoye2016increasing], which varies between areas [@strine2010geographic], and drink-driving in the past year among drivers (expected to raise injuries), both from the Community Health Survey [@kang2015korea]. "
 "Socioeconomic conditions were represented by the share of basic livelihood security recipients (expected to raise injuries) and the tertiary-educated share of adults (expected to lower them) [@hosking2013ethnic; @branioncalles2026evaluating]. "
 "Five controls were forced into every model: urban population share, physicians per 1,000 residents, sex ratio, fiscal autonomy and the share of the total population aged 80 years or older, a partial proxy for the age structure of the older population. "
 "Three negative control exposures without a plausible causal relation to road injury (awareness of cardiopulmonary resuscitation, fires per 10,000 residents and the share of deaths with ill-defined causes) were fitted in a separate model [@lipsitch2010negative]. All characteristics were standardised to mean 0 and standard deviation (SD) 1."),
("Statistical analysis",
 f"Five likelihoods (Poisson, negative binomial, zero-inflated Poisson, zero-inflated negative binomial and Poisson with an observation-level random effect) were compared with the same random effects and the forced controls ({sup('lik')}). "
 f"The rule fixed before any covariate model was fitted compared Poisson and negative binomial only and chose the one with the lower widely applicable information criterion (WAIC) for the forced-control model (negative binomial, {LIKF['nbinomial']['WAIC']:,.1f} versus {LIKF['poisson']['WAIC']:,.1f}) [@gelman2014understanding]. "
 "The Poisson model with an observation-level effect had a lower WAIC but a worse logarithmic score and was fitted as an alternative specification. "
 "The principal model had an offset of log expected counts, a Besag–York–Mollié 2 district effect with penalised-complexity priors [@besag1991bayesian; @riebler2016intuitive; @simpson2017penalising] and first-order random-walk and independent year effects, and was fitted by integrated nested Laplace approximation in R 4.6.0 [@rue2009approximate; @web:rcore2026] (prior settings in Appendix A). "
 "Rate ratios (RRs) per 1 SD increase are reported with 95% credible intervals (CrIs), and an association was called credible when its interval excluded 1; P values were not used to judge associations. "
 "Residual hot spots and cold spots were districts whose posterior probability of a residual spatial RR above 1 exceeded 0.95 or fell below 0.05 (exploratory, not adjusted for multiple comparisons). "
 "Persistence of district rankings was measured by Kendall's W over the 14 annual SIRs and by Spearman correlations of period ratios between 2011–2015, 2016–2019 and 2020–2024; spatial autocorrelation by Moran's I with permutation tests (two-sided for residuals) [@moran1950notes].",
 f"Robustness was assessed in all {N['mv_total']} models formed by every non-empty subset of the seven characteristics (robust when credible in at least 75% of the models containing the characteristic with at least 95% sign agreement) [@steegen2016increasing]; the four Knorr-Held space-time interactions (type I, unstructured district by unstructured year; type II, unstructured district by random-walk year; type III, structured district by unstructured year; type IV, structured by structured) [@knorrheld2000bayesian]; refits in the three periods and an interaction with the period from 2020; alternative temporal structures, lags, a Spatial+-type adjustment and restricted spatial regression for spatial confounding [@dupont2022spatial], survey smoothing and extreme values; omission of each province and each year; a different adjacency graph, omission of the share aged 80 years or older and expected counts from the total population ({sup('specs')}). "
 "Because a high rate per older resident could reflect heavy traffic from visitors and through-traffic, three further analyses were specified before fitting: exclusion of the tenth of districts with the highest all-crash rate per resident, adjustment for the logarithm of that rate, and crash-based expected counts (also with adjustment for the older share of residents). "
 "Associations in the direction opposite to that expected were examined post hoc with these existing fits only, without changing the principal model. "
 "Spearman correlation with transport-injury deaths of all ages (ICD-10 V01–V99) by district of residence over 2011–2024, from cause-of-death statistics [@web:kostat2026cause], described how far the geography matched that of fatal transport injury."),
]

EN = {"서울시": "Seoul", "경기도": "Gyeonggi-do", "충청남도": "Chungcheongnam-do", "충청북도": "Chungcheongbuk-do", "부산시": "Busan", "전라남도": "Jeollanam-do", "전라북도": "Jeollabuk-do", "광주시": "Gwangju", "인천시": "Incheon",
      "경상남도": "Gyeongsangnam-do", "경상북도": "Gyeongsangbuk-do", "강원도": "Gangwon-do", "대구시": "Daegu", "대전시": "Daejeon", "울산시": "Ulsan", "제주도": "Jeju", "세종시": "Sejong"}
def sidos(d, k=4):
    l = [f"{EN[a]} ({b})" for a, b in list(d.items())[:k]]; return ", ".join(l[:-1]) + " and " + l[-1]
NAT = N["nat"]; LIKF = N["lik"]; NB = LIKF["nbinomial"]; POI = LIKF["poisson+obs_iid"]
X = lambda a, v: N["s69s"][(a, v)]
TOP = [a for a in N["s69s_waic"] if a.startswith("exclude_top10pct")][0]
CR = lambda v: (lambda r: (r.IRR, r.lo, r.hi))(N["s10"].set_index("cov").loc[v])
CRO = lambda v: X("E_per_crash_plus_older_share", v)
def mvp(v): return f"{100 * N['mv'][v]['cred_frac']:.0f}%"
RESULTS = [
("National counts and rates",
 f"Police recorded {N['cases_total']:,} injured people aged 65 years or older in road traffic crashes over 2011–2024. "
 f"The annual number rose from {D['inj_2011']:,} in 2011 to {D['inj_2019']:,} in 2019, fell to {D['inj_2020']:,} in 2020 and reached {D['inj_2025']:,} in 2025, the highest of the series (Fig. 1a). "
 f"The rate per 100,000 residents aged 65 years or older peaked at {NAT.loc[D['peak_rate_year'], 'rate_per100k_65']:.0f} in {D['peak_rate_year']}, was {D['rate_2019']:.0f} in 2019 and {D['rate_2020']:.0f} in 2020, and was {D['rate_2025']:.0f} in 2025 (Fig. 1b), while the population aged 65 years or older grew from {D['pop65_2011']/1e6:.1f} million to {D['pop65_2025']/1e6:.1f} million. "
 f"Injured older people per 100 police-reported crashes of any kind rose from {D['share_inj_of_allcrash_2011']:.1f} in 2011 to {D['share_inj_of_allcrash_2024']:.1f} in 2024 and {NAT.loc[2025, 'injured_per_crash100']:.1f} in 2025 (Fig. 1c). Table 1 summarises the counts and district characteristics by period.",
 "@@F1", "@@T1"),
("Geography and its persistence",
 f"The 10th and 90th percentiles of district SIRs over 2011–2024 were {T1['ALL']['p10']:.2f} and {T1['ALL']['p90']:.2f} (ratio {D['p90p10_all']:.2f}). "
 f"Moran's I of the pooled log SIR was {N['moran_pooled']:.2f} (permutation P = 0.001), and annual values ranged from {N['moran_year'][0]:.2f} to {N['moran_year'][1]:.2f}. "
 f"District rankings were stable: Spearman correlations between periods ranged from {D['rho_win_min']:.2f} to {D['rho_win_max']:.2f}, Kendall's W over the 14 years was {N['kendall']['2011-2024']:.2f}, and the 2025 ranking correlated with that of 2024 ({D['rho_2024_2025']:.2f}). "
 f"After adjustment, the principal model identified {N['n_hot']} residual hot spots, mainly in {sidos(N['hot_by_sido'])}, and {N['n_cold']} cold spots, of which {N['metro_cold']} were among the {N['n_metro']} districts of Seoul, Busan and Incheon (Fig. 2c; {sup('hot')}). "
 f"The structured share of the district effect was {N['phi'][0]:.2f} (95% CrI {N['phi'][1]:.2f}–{N['phi'][2]:.2f}), and there was no evidence of positive residual spatial autocorrelation (Moran's I {N['moran_resid']:.3f}, expected {N['moran_resid_exp']:.3f}, two-sided P = {N['moran_resid_p']:.2f}). "
 f"The SIRs correlated moderately with the standardised mortality ratios of transport-injury deaths of all ages by place of residence (Spearman {D['rho_trans']:.2f}).",
 "@@F2"),
("Rates per older resident and per crash",
 f"The SIR per older resident correlated strongly with the district rate of all police-reported crashes per 1,000 residents (Spearman {D['rho_smr_allcrash_rate']:.2f}) and weakly with the share of the population aged 65 years or older ({D['rho_smr_oldshare']:.2f}). "
 f"The crash-based ratio showed the opposite pattern: it correlated with the older population share ({D['rho_crash_oldshare']:.2f}) but hardly with the crash rate ({D['rho_smrcrash_allcrash_rate']:.2f}). "
 f"The two ratios correlated at {D['rho_std_crash']:.2f}, and only {int(D['top_decile_overlap'])} of the 23 districts in the top tenth by one ratio were also in the top tenth by the other (Fig. 2a, b). "
 f"The crash-based ratio was also stable, with Spearman correlations of {D['rho_crash_win_min']:.2f}–{D['rho_crash_win_max']:.2f} between periods."),
("District characteristics",
 f"The negative binomial likelihood fitted better than the Poisson (WAIC {NB['WAIC']:,.1f} versus {LIKF['poisson']['WAIC']:,.1f}); no district-year had zero injuries, zero-inflated versions did not improve the fit, and the Poisson model with an observation-level effect had a lower WAIC ({POI['WAIC']:,.1f}) and a worse logarithmic score ({POI['neg_logscore']:,.1f} versus {NB['neg_logscore']:,.1f}) ({sup('lik')}). "
 f"In the principal model (WAIC {MAIN_WAIC:,.1f}), injured older people were more numerous with more registered motor vehicles per resident ({ci(CAR)}) and less numerous with a higher traffic culture index ({ci(TCI)}) and a larger tertiary-educated share ({ci(TE)}) (Table 2). "
 "The 95% CrIs for the paved share of roads, driver seat-belt wearing, drink-driving and basic livelihood receipt included 1, as did those for the three negative control exposures. "
 "Vehicles per resident and the tertiary-educated share were credible in each of the three periods, and the traffic culture index in 2011–2015 and 2020–2024. "
 f"The three were credible in {mvp(CAR)}, {mvp(TCI)} and {mvp(TE)}, respectively, of the {N['mv']['ext__cars_per_capita']['n_specs']} covariate subsets that contained each of them, with complete sign agreement, and remained credible in {N['ret'][CAR][0]}, {N['ret'][TCI][0]} and {N['ret'][TE][0]} of {N['ret'][CAR][1]} alternative fits (Table A3); the CrI included 1 for vehicles when Busan was omitted and for the tertiary-educated share when Gyeonggi-do or 2011 was omitted. "
 f"With the best-fitting space-time interaction (Knorr-Held type II; WAIC {N['s43_waic']['KH_typeII']:,.1f} versus {MAIN_WAIC:,.1f} for the principal model), vehicles per resident ({tci(S43('KH_typeII', CAR))}) and the tertiary-educated share ({tci(S43('KH_typeII', TE))}) remained associated, whereas the traffic culture index was attenuated towards 1 ({tci(S43('KH_typeII', TCI))}); it remained associated with the type III interaction ({tci(S43('KH_typeIII', TCI))}). "
 f"The Spatial+-type adjustment and restricted spatial regression left all three associations credible (Table A3). District characteristics explained {100 * N['vp']['fixed_hypothesis']:.1f}% of the variance of the linear predictor and the structured district effect {100 * N['vp']['spatial_structured']:.1f}%.",
 "@@T2"),
("Crash rate and crash-based expected counts",
 f"Excluding the {len(N['s69s_top'])} districts with the highest crash rates left the three associations credible (vehicles {tci(X(TOP, CAR))}; traffic culture {tci(X(TOP, TCI))}; tertiary education {tci(X(TOP, TE))}). "
 f"Adding the logarithm of the all-crash rate, itself strongly associated with the outcome ({tci(X('plus_all_crash_rate', 'acc_z'))}), lowered the WAIC by {N['s69s_waic']['refit_principal'] - N['s69s_waic']['plus_all_crash_rate']:,.0f} and moved the traffic culture index ({tci(X('plus_all_crash_rate', TCI))}) and the tertiary-educated share ({tci(X('plus_all_crash_rate', TE))}) to 1; vehicles per resident ({tci(X('plus_all_crash_rate', CAR))}) and basic livelihood receipt ({tci(X('plus_all_crash_rate', BLS))}) moved to inverse associations. "
 f"With crash-based expected counts, the CrI for vehicles per resident included 1 ({tci(CR(CAR))}); a larger tertiary-educated share ({tci(CR(TE))}), a higher traffic culture index ({tci(CR(TCI))}) and a larger paved share ({tci(CR(PAVE))}) were associated with fewer injured older people per crash, and a larger share of basic livelihood recipients with more ({tci(CR(BLS))}). "
 f"After adjustment for the older share of residents ({tci(CRO('old_z'))}), the tertiary-educated share ({tci(CRO(TE))}) remained associated, the traffic culture index ({tci(CRO(TCI))}) and paved share ({tci(CRO(PAVE))}) remained weakly associated, and the CrI for basic livelihood receipt included 1 ({tci(CRO(BLS))}). "
 f"With expected counts from the total population and without the share aged 80 years or older, the three associations remained credible in the same direction; the association with the tertiary-educated share was stronger with total-population expected counts ({tci(SEN('sc', TE))}) (Fig. 3; Table A3).",
 "@@F3"),
]

if __name__ == "__main__":
    for x in METHODS: print("##", x[0]); [print(p, "\n") for p in x[1:]]
