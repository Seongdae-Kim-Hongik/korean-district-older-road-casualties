# Older road casualties and crash geography across Korean districts

Analysis code for a manuscript on injured road users aged 65 years or older in police-reported road traffic crashes, counted by the district of crash occurrence, across 229 districts of the Republic of Korea, 2011-2024 (national series to 2025).

Archived version: Zenodo, https://doi.org/10.5281/zenodo.24391308 (v1.0.2).

## Contents

This repository contains code only. The processed district-year data (analytic panel, expected counts, covariate pool, result tables, adjacency graph and boundary file) are not included; they are available from the author on reasonable request. All source statistics are public (see Data sources).

| Path | What it is |
|---|---|
| `01_스크립트/` | Analysis scripts (below) |
| `04_분석/ELTI/sets_ELTI_std3.json`, `sets_ELTI_s577.json`, `sets_ELTI_s2.json`, `sets_ELTI_sc.json`, `config_ELTI_std3.json`, `make_sets_elti.py`, `run_std3_chain.sh`, `run_std3_resume.sh`, `run_sens3.sh` | Covariates with expected directions, forced controls, negative controls and model settings (principal model `std3`; sensitivity versions with the queen contiguity graph, without the share aged 80 or older, and with expected counts from the total population) |
| `04_분석/ELTI/MS/build/` | Scripts that read the result tables and write every number, table and figure in the manuscript and appendix, including `content_elti.py`, which generates the Methods and Results text |

Folder and some column names are in Korean because the source tables are Korean; each script has a header comment describing its inputs and outputs.

## Data sources

All inputs are public, aggregated statistics. No individual-level data are included.

- Road traffic crashes involving people aged 65 years or older (crashes, deaths, injured people) by district of crash occurrence: National Police Agency via Korean Statistical Information Service (KOSIS) local indicators (DT_1YL202108), 2011-2025.
- Population aged 65 years or older and total population by district: resident registration via KOSIS (DT_1YL20631).
- Registered motor vehicles per resident (DT_1YL20731), drink-driving crashes and all crashes (DT_1YL14001, DT_1YL13901): KOSIS local indicators.
- District covariates: a harmonized public district panel (urban population share, physicians, sex ratio, fiscal autonomy, share aged 80+, basic livelihood security recipients with corrected cells, tertiary education, road pavement, traffic culture index, fires) and the Community Health Survey (driver seat-belt wearing, drink-driving, awareness of cardiopulmonary resuscitation).
- KOSIS tables are fetched by `99E_elti_fetch.py`, which requires a personal KOSIS API key in `~/.kosis_key` (not included).

## Pipeline

Run from the repository root (set `ST_DATA_ROOT` and `ST_GPT_DATASET` to the local copies of the public source files and the read-only district database).

| Step | Script | Output |
|---|---|---|
| 0 | `99E_elti_fetch.py` | KOSIS tables 2011-2025 |
| 1 | `99E_elti_build.py`, `99E_elti_pool.py` | Outcome counts by district code (general wards summed, boundary changes assigned), population aged 65+, expected counts (per older resident; per crash), checks against national totals; district characteristics |
| 2 | `99E_elti_desc.py` | National series 2011-2025, period ratios, denominator comparison, comparison with transport-injury deaths |
| 3 | `80_build_disease_panel_v.py ELTI` (`ST_VER=std3`) | Analytic panel |
| 4 | `69K_elti_likelihood.R` | Likelihood comparison (Poisson, negative binomial, zero-inflated, observation-level effect) |
| 5 | `81_fit_inla.R ELTI` (`ST_VER=std3`, `ST_GRAPH=04_분석/ELTI/graph_593.graph`, `ST_THREADS=1`; wrapped in `rslot.sh`) | Principal model, set comparison, 200-subset multiverse, window models, expected-count sensitivity |
| 6 | `85_window_maps.R`, `86_yearly_maps_ehsa.py`, `86b_ehsa_modified_mk.py`, `87_window_grid.py` | Maps, yearly smoothed ratios, persistence and emerging hot spot analysis |
| 7 | `88g_sens_prep.py ELTI std3`, `88g_sens_suite.R` (`GROUP=1..6`), `88h_ppc_varpart.R`, `88k_struct_kh.R` (nb, struct, kh, review, conf) with `kh_constraints.R`, `89g_sens_combine.py` | Sensitivity analyses, Knorr-Held models, Spatial+ and restricted spatial regression |
| 8 | `04_분석/ELTI/MS/build/` (`build_refs_elti.py`, `figs_elti.py`, `build_manuscript_elti.py`, `appendix_elti.py`; `run_all_elti.sh`) | Manuscript, appendix, figures and checks |

The boundary file is found at `data/boundary/final.shp` by default; set `ST_SHP` to use another path.

## Software

R 4.6.0 with R-INLA 25.10.19, spdep and sf; Python 3.9 with pandas, geopandas, numpy, scipy, matplotlib and python-docx.

## Licence

MIT (see `LICENSE`).
