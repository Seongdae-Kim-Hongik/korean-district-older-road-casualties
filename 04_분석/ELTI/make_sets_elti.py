#!/usr/bin/env python3
# ELTI (injured older road users, place of occurrence) chain
import json, hashlib, os
POOL = "EXT_canonical_pool_ELTI_261119.csv"
forced = ["ext__urban_population_share", "ext__physicians_per_1000", "ext__sex_ratio", "ext__fiscal_independence", "ext__pop80_share"]
neg = ["ext__cpr_awareness_rate", "ext__fires_per_10000", "ext__ill_defined_share"]
sens = ["ext__living_alone_elderly", "ext__all_crash_per1000", "ext__em_specialists_per100k", "ext__drink_drive_crash_share"]
S1 = ["ext__cars_per_capita", "ext__road_pavement_rate", "ext__traffic_culture_index", "ext__seatbelt_rate", "ext__drink_driving_rate",
      "ext__basic_livelihood_rate", "ext__tertiary_educated_share"]
sets = {"S1_narrative_full": S1,
        "S2_core": ["ext__cars_per_capita", "ext__traffic_culture_index", "ext__basic_livelihood_rate"],
        "S3_road_environment": S1[:2], "S4_road_user_behaviour": S1[2:5], "S5_socioeconomic": S1[5:], "S6_road_environment_behaviour": S1[:5]}
allv = forced + neg + sens + S1
assert "ext__living_alone_elderly" in allv
ext = {v: [POOL, v[5:]] for v in allv}; ext["ext__elti_cases"] = ["ELTI_E69.csv", "cases"]; ext["ext__pop65"] = ["ELTI_E69.csv", "pop65"]
tr = {v: "none" for v in allv}; tr["ext__cars_per_capita"] = "log"
dirs = {"ext__cars_per_capita": "+ (1인당 자동차 등록, 로그: 차량 노출·차량 의존 이동)",
        "ext__road_pavement_rate": "± (도로포장률: 포장 도로 = 통행 속도·교통량 증가(+) 대 노면 안전(−))",
        "ext__traffic_culture_index": "- (교통문화지수: 운전·보행 행태·교통안전 종합)",
        "ext__seatbelt_rate": "- (운전자석 안전벨트 착용률 KCHS: 안전 행동 규범)",
        "ext__drink_driving_rate": "+ (운전자 연간 음주운전 경험률 KCHS: 고위험 운전)",
        "ext__basic_livelihood_rate": "+ (기초생활 수급률, 2021-23 정정: 박탈 → 보행 의존·안전 시설 부족)",
        "ext__tertiary_educated_share": "- (대졸 이상 비율: 지역 사회경제 수준)"}
base = dict(tag="ELTI", outcome_column="ext__elti_cases",
  outcome_label_en="Injured casualties aged 65 years or older in police-reported road traffic crashes, counted by district of crash occurrence (National Police Agency, via KOSIS e-local indicators DT_1YL202108), annual",
  disease_en="Older-adult road traffic injury (place of occurrence)", disease_ko="노인(65+) 교통사고 부상자(발생지)",
  pathway="노인 도로이용 안전 내러티브(차량 노출·도로 환경·도로이용 행태·사회경제).",
  forced=forced, negative_controls=neg, offset_E_column="E_std", offset_E_file="ELTI_E69.csv", offset_E_sensitivity_column="E_crash",
  offset_E_label="expected injured older adults = resident population aged 65+ (resident registration, DT_1YL20631) x national annual rate; sensitivity E = all police-reported crashes in the district x national ratio",
  graph="593-edge contact graph, ST_GRAPH=04_분석/ELTI/graph_593.graph",
  population_override=[{"year": 2023, "fbd_region": "경상남도창원시", "population": 1009038, "source": "KOSIS DT_1YL20651E 2023 통합창원시 계(유방암 11/4 population_final_audit)"}],
  sensitivity_only_extra=sens,
  version="std3 older road-user safety narrative (vehicle exposure, road environment, road-user behaviour, socioeconomic), 2011-2024",
  fixed_on="2026-11-19 (공변량 모형 적합 전 고정; 독거노인은 80+ 비율과 VIF 16 → 민감도 전용)",
  sets=sets, transform=tr, expected_direction=dirs, evidence={v: "(문헌 단계 manifest에서 PMID 연결)" for v in S1},
  rules=dict(likelihood="forced-only 모형 WAIC 낮은 쪽(Poisson/NB)", set_choice="WAIC 최소, 4 이내면 변수 적은 세트", credible="95% CrI 1 제외", vif_drop=10, multiverse_specs=200,
             main_model_note="주모형 = S1_narrative_full(가설 7 + 강제통제 5). 세트를 다시 바꾸지 않음. VIF>10 유지·보고. 발생지 노출은 E_crash(81 S10)·전체 사고율 추가(88g)·관광·통과 상위 10% 제외 민감도.",
             years=[2011, 2024], windows={"W1_2011-15": [2011, 2015], "W2_2016-19": [2016, 2019], "W3_2020-24": [2020, 2024]}, covid_post_from=2020),
  note="ELTI = 경찰청 집계 노인(65+) 교통사고 부상자(중상·경상·부상신고), 사고 발생지 시군구. 사망자 열이 공식 65+ 교통사고 사망자(2018 1,682)와 일치 → 노인 사상자 기준(노인 운전자 사고 아님). 2011-2025 수집, 공변량이 2024까지라 모형 2011-2024, 2025는 기술만. 세종 2013-25·연기군 2011-12 원표, 청주=청주+청원(2011-13). 시군구 합=전국 15년.",
  extra_columns=ext)
for V, extra in (("std3", {}), ("s577", {}), ("s2", {"forced": forced[:4], "sens_note": "민감도: 80세 이상 비율 강제통제 없음"}), ("sc", {"offset_E_column": "E_crude", "offset_E_sensitivity_column": None})):
    d = dict(base); d.update(extra); d = {k: v for k, v in d.items() if v is not None}
    f = f"sets_ELTI_{V}.json"; json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(V, hashlib.sha256(open(f, "rb").read()).hexdigest())
