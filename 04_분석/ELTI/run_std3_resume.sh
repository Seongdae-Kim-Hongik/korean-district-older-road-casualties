#!/bin/bash
# ELTI (injured older road users, place of occurrence) chain
set -x
S="${ST_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"; cd "$S"; export SK_RSLOTS=7; RS="nice -n 10 $S/01_스크립트/rslot.sh"
GR="$S/04_분석/ELTI/graph_593.graph"; T=ELTI; D=261119; L="$S/04_분석/$T"
wl(){ while true; do l5=$(sysctl -n vm.loadavg | awk '{print $3}'); awk -v l=$l5 'BEGIN{exit !(l>=14)}' || break; echo "load5=$l5 ≥14 wait 10m $(date +%H:%M)"; sleep 600; done; }
q(){ while [ "$(jobs -rp | wc -l)" -ge 2 ]; do sleep 15; done; }
export ST_VER=std3 ST_THREADS=1 ST_GRAPH="$GR"
wl; (cd 01_스크립트 && ST_MV_N=127 $RS Rscript 81_fit_inla.R $T) > $L/run_std3_81a2.log 2>&1 || exit 1
ls $L/results_std3/S7_multiverse_summary.csv || { echo "81 미완 — 중단"; exit 1; }
echo STAGE81_done
python3 01_스크립트/82_core_report.py $T $D > $L/run_std3_82.log 2>&1; echo "82 rc=$?"
python3 01_스크립트/83_check_report.py $T $D >> $L/run_std3_82.log 2>&1
python3 01_스크립트/87_window_grid.py $T std3; (cd 01_스크립트 && TAG=$T ST_VER=std3 $RS Rscript 85_window_maps.R $T std3); python3 01_스크립트/86_yearly_maps_ehsa.py $T std3
python3 01_스크립트/88g_sens_prep.py $T std3 || exit 1
cd 01_스크립트; export TAG=$T
for G in 1 2 3 4 5 6; do q; wl; GROUP=$G $RS Rscript 88g_sens_suite.R > $L/run_std3_88g_$G.log 2>&1 & sleep 5; done
q; wl; $RS Rscript 88h_ppc_varpart.R > $L/run_std3_88h.log 2>&1 &
for G in nb struct kh review conf; do q; wl; $RS Rscript 88k_struct_kh.R $G > $L/run_std3_88k_$G.log 2>&1 & sleep 5; done
wait
if grep -q 'KH_type.* FAILED' $L/run_std3_88k_kh.log; then KH_INIT=0 $RS Rscript 88k_struct_kh.R kh > $L/run_std3_88k_kh_init0.log 2>&1; fi
$RS Rscript 88k_struct_kh.R combine > $L/run_std3_88k_combine.log 2>&1
cd ..; TAG=$T ST_VER=std3 python3 01_스크립트/89g_sens_combine.py $T std3 > $L/run_std3_89g.log 2>&1
echo CHAIN_MAIN_done
# s577·s2·sc는 run_sens3.sh로 따로(11/19 14:05 시작)
echo "ALL rc=$?"; grep -l "FAILED\|Error" $L/run_std3_8*.log; true
