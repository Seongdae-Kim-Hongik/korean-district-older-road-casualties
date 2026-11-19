#!/bin/bash
# ELTI (injured older road users, place of occurrence) chain
S="${ST_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"; cd "$S"; export SK_RSLOTS=7; RS="nice -n 10 $S/01_스크립트/rslot.sh"; GR="$S/04_분석/ELTI/graph_593.graph"; T=ELTI; L="$S/04_분석/$T"
for V in s577 s2 sc; do ST_VER=$V python3 01_스크립트/80_build_disease_panel_v.py $T > $L/run_${V}_80.log 2>&1 && (cd 01_스크립트 && ST_VER=$V ST_THREADS=1 ST_MV_N=2 ST_GRAPH=$([ $V = s577 ] || echo "$GR") $RS Rscript 81_fit_inla.R $T) > $L/run_${V}_81.log 2>&1; echo "$V rc=$?"; done
echo SENS_done
