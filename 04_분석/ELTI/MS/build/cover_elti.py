# cover_elti.py — ELTI 커버레터·하이라이트(JSR). 단독 저자 명의, 심사자 정보는 넣지 않음, 자료 중복 고지 없음.
import os, subprocess
from build_jsr_elti import TX, TITLE, AFFIL, EMAIL, PHONE, OUT, N
import content_elti as C
D = N["desc"]
HL = ["Injured older road users in Korea hit a record 46,021 in 2025 as the population aged",
      "District rates per older resident moved with the overall crash rate (Spearman 0.88)",
      "Injured older people per crash moved with the older population share (Spearman 0.94)",
      "The two denominators ranked districts differently (correlation 0.36)",
      "More vehicles, weaker traffic culture and less education marked high-rate districts"]
for h in HL: assert len(h) <= 85, (len(h), h)
J = TX(cite="ay")
J.para("19 November 2026"); J.para("The Editor, Journal of Safety Research", before=8)
J.para("Dear Editor,", before=8)
for p in [f"I submit the research article \"{TITLE}\" for consideration in the Journal of Safety Research.",
          f"Police statistics count road casualties where crashes occur, whereas rates are expressed per resident. Using all {N['n_districts']} districts of the Republic of Korea over 2011–2024 and {N['cases_total']:,} injured road users aged 65 years or older, the study shows that the district ranking depends on the denominator: rates per older resident moved with the overall crash rate of a district (Spearman 0.88), whereas injured older people per crash moved with population ageing (0.94), and the two measures ranked districts differently. Vehicles per resident, the traffic culture index and the tertiary-educated share were associated with the rate per older resident across all 127 covariate subsets and most alternative models, but not after adjustment for the all-crash rate, which the manuscript interprets cautiously.",
          "The findings speak directly to practitioners who rank districts for older road-user safety programmes, and the manuscript closes with practical applications as the journal requests. The analysis code is openly archived; the data are public aggregate statistics.",
          "The manuscript is original, has not been published and is not under consideration elsewhere, and if accepted it will not be published elsewhere in the same form. The author declares no competing interests and received no specific funding. The manuscript has been prepared for double-anonymized review; author details are on the separate title page.",
          "Thank you for considering this submission."]:
    J.para(p, before=8)
J.para("Sincerely,", before=8); J.para("Seongdae Kim, PhD"); J.para(AFFIL); J.para(f"Email: {EMAIL}; Phone: {PHONE}")
J.doc_title = ""; J.save(os.path.join(OUT, "Cover_letter.docx"))
H = TX(cite="ay"); H.para("<b>Highlights</b>")
for h in HL: H.para(f"• {h}")
H.doc_title = ""; H.save(os.path.join(OUT, "Highlights.docx"))
open(os.path.join(OUT, "Cover_letter_paste.txt"), "w").write("\n\n".join([p.text for p in J.doc.paragraphs]))
for f in ("Cover_letter.docx", "Highlights.docx"):
    subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_elti_jsr", "--convert-to", "pdf", "--outdir", OUT, os.path.join(OUT, f)], check=True, capture_output=True)
print("cover/highlights ok")
