#!/bin/bash
# run_all_elti.sh — ELTI 원고 빌드(refs → figures → manuscript·title page → appendix → sanitize → checks)
set -e; cd "$(dirname "$0")"
python3 build_refs_elti.py >/dev/null
python3 figs_elti.py
python3 build_jsr_elti.py
python3 appendix_elti.py
python3 sanitize_docx.py ../out/Manuscript_anonymized.docx ../out/Supplementary_Material_Appendix_A.docx
python3 sanitize_docx.py --no-anon ../out/Title_page.docx
for f in Manuscript_anonymized Title_page Supplementary_Material_Appendix_A; do /opt/homebrew/bin/soffice --headless -env:UserInstallation=file:///tmp/lo_elti_jsr --convert-to pdf --outdir ../out ../out/$f.docx >/dev/null 2>&1; done
python3 check_elti.py
