# check_elti.py — ELTI 투고 전 기계 점검: 초록 단어·소제목, 키워드-제목 중복, 익명성(저자명·기관·저장소 링크), 본문 인용 ↔ 참고문헌 1:1, 참고문헌 알파벳순, 표 3선(XML), 쌍점 없는 제목.
import os, re, json, sys
from docx import Document
import build_jsr_elti as B
OUT = B.OUT; bad = []
D = B.read_draft(); ab = "\n".join(D["Abstract"])
heads = re.findall(r"^(Introduction|Method|Results|Conclusions|Practical Applications):", ab, re.M); words = len(ab.split())
if heads != ["Introduction", "Method", "Results", "Conclusions", "Practical Applications"]: bad.append(("abstract headings", heads))
if words > 300: bad.append(("abstract words incl. headings", words))
tw = {w.lower().strip(",.") for w in B.TITLE.split()}
for k in B.C.KEYWORDS:
    rep = [w for w in k.lower().split() if w in tw and w not in {"of", "and", "the", "in"}]
    if rep: bad.append(("keyword repeats title word", k, rep))
if len(B.C.KEYWORDS) < 5: bad.append(("keywords < 5", len(B.C.KEYWORDS)))
if ":" in B.TITLE: bad.append(("colon in title", B.TITLE))
M = Document(os.path.join(OUT, "Manuscript_anonymized.docx")); txt = "\n".join(p.text for p in M.paragraphs) + "\n".join(c.text for t in M.tables for r in t.rows for c in r.cells)
for pat in ("Seongdae", "Kim S", "Hongik", "kimsd", "zenodo", "github", "7002340", "0000-0002-1525-0091"):
    if pat.lower() in txt.lower(): bad.append(("anonymity", pat))
for d in (M, Document(os.path.join(OUT, "Supplementary_Material_Appendix_A.docx"))):
    cp = d.core_properties
    if (cp.author or "").strip() or (cp.last_modified_by or "").strip(): bad.append(("docx author metadata", cp.author, cp.last_modified_by))
refs = open(os.path.join(OUT, "reference_list.txt")).read().strip().split("\n")
if len(refs) != len(B.KEYS): bad.append(("ref count", len(refs), len(B.KEYS)))
keyorder = sorted(B.KEYS, key=B.sortkey)
if [B.aref(k) for k in keyorder] != refs: bad.append(("ref order/content mismatch",))
for tb in M.tables:
    x = tb._tbl.xml
    if "w:insideV" in x and 'w:val="single"' in x.split("w:insideV")[1][:60]: bad.append(("table vertical lines",))
print("CHECK:", "PASS" if not bad else "FAIL"); [print(" -", b) for b in bad]; print(f"abstract {words} words; refs {len(refs)}; keywords {len(B.C.KEYWORDS)}")
sys.exit(1 if bad else 0)
