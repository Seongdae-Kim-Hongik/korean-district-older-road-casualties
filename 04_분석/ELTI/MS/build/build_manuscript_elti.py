# build_manuscript_elti.py — ELTI 투고 원고 조립(the journal, Research paper, 2026-11-20).
#  the journal 규정(Guide for authors 원문 11/20 확인): 이중 익명(제목면 별도), 3000–6000단어, 초록 ≤250 비구조, 키워드 1–7, 하이라이트 3–5개 ≤85자(별도 파일),
#   'accident' 단어 금지(인용 문헌 제목만 예외), 약어 최소화, 수가 아닌 비율, Elsevier Harvard 참고문헌(본문 저자-연도, 두 저자 'and', 목록 알파벳순, LTWA 약어).
import os, re, json, subprocess
from docx.shared import Pt, Mm
from jkms_engine import JKMS
import content_elti as C
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_elti.json"), encoding="utf-8"))
DRAFT = os.path.join(MS, "draft", "02_manuscript.md")
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "[ZENODO DOI]"
TITLE = C.TITLE; ORCID = "0000-0002-1525-0091"
AFFIL = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
EMAIL = "kimsd@hongik.ac.kr"; PHONE = "+82-2-320-1114"
FUNDING = "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors."
COI = "Declarations of interest: none."
AI_HEAD = "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process"
AI_STATEMENT = ("During the preparation of this work the author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript. "
                "After using these tools, the author reviewed and edited the content as needed and takes full responsibility for the content of the published article.")
IRB_FULL = ("The Institutional Review Board of Hongik University approved the study on 4 November 2025 (7002340-202511-HR-012) and its continuing review on 3 November 2026 (7002340-202611-HR-040) "
            "and waived informed consent because only published aggregate statistics were used.")
IRB_ANON = "The institutional review board of the author's institution approved the study and waived informed consent because only published aggregate statistics were used (details on the title page)."
def data_full(): return (f"All source data are publicly available aggregate statistics cited in the Materials and methods. The analysis code that generates every number, table and figure is openly available on Zenodo (https://doi.org/{ZENODO}) under the MIT License. "
                         "The processed district-year data are available from the author on reasonable request.")
DATA_ANON = ("All source data are publicly available aggregate statistics cited in the Materials and methods. The analysis code is openly available in a public repository under the MIT License; its persistent identifier is given on the title page to preserve anonymized review. "
             "The processed district-year data are available from the author on reasonable request.")
ACK = "None."
CREDIT = "Seongdae Kim: Conceptualization, Data curation, Formal analysis, Investigation, Methodology, Software, Validation, Visualization, Writing – original draft, Writing – review & editing."

def read_draft():
    md = open(DRAFT, encoding="utf-8").read(); md = re.sub(r"<!--.*?-->", "", md, flags=re.S); S = {}; cur = None
    for line in md.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m: cur = m.group(1).strip(); S[cur] = []; continue
        if cur is not None: S[cur].append(line)
    return {k: [p.strip() for p in "\n".join(v).split("\n\n") if p.strip()] for k, v in S.items()}
def cites(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: " {{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
def all_keys():
    src = open(os.path.join(HERE, "content_elti.py"), encoding="utf-8").read() + open(DRAFT, encoding="utf-8").read()
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S); src = re.sub(r"(?m)^\s*#.*$", "", src)
    return sorted(k for k in {k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")} if re.fullmatch(r"(web:)?[a-z][a-z0-9]*", k))
KEYS = all_keys(); _miss = [k for k in KEYS if k not in REFS]; assert not _miss, _miss

# ── 저자-연도 라벨(Elsevier Harvard) ──
KEEP = {"Korea", "Korean", "Seoul", "Japan", "Japanese", "Sydney", "Auckland", "Wisconsin", "Chicago", "Toronto", "Balearic", "Islands", "Corfu", "Sweden", "Swedish", "Norway", "Daegu", "Victoria", "Australia", "Canada",
        "British", "Columbia", "New", "Zealand", "United", "States", "U.S.", "COVID-19", "Bayesian", "Laplace", "Spatial+", "Besag", "STROBE", "Moran", "I", "Global", "Burden", "Disease", "Study", "R", "Yoon's", "Act", "England", "Taiwan", "DRIVE", "OECD", "WHO"}
def sent(t):
    w = t.split(" "); caps = sum(1 for x in w[1:] if x[:1].isupper())
    if len(w) < 4 or caps < 0.5 * (len(w) - 1): return t
    out = [w[0]]
    for x in w[1:]:
        core = x.strip("(),:;.?[]\"'")
        keep = core in KEEP or core.isupper() or any(c.isdigit() for c in core) or out[-1].endswith((":", "?"))
        out.append(x if keep else x[:1].lower() + x[1:])
    return " ".join(out)
SMALL = {"of", "and", "the", "in", "for", "on", "a", "an", "to"}
JFIX = {"Accident; analysis and prevention": "Accident Analysis & Prevention", "Injury prevention : journal of the International Society for Child and Adolescent Injury Prevention": "Injury Prevention",
        "PloS one": "PLOS ONE", "Lancet (London, England)": "The Lancet", "BMC public health": "BMC Public Health", "Age and ageing": "Age and Ageing", "Human factors": "Human Factors",
        "Australian and New Zealand journal of public health": "Australian and New Zealand Journal of Public Health", "Statistics in medicine": "Statistics in Medicine",
        "Statistical methods in medical research": "Statistical Methods in Medical Research", "Journal of the American Geriatrics Society": "Journal of the American Geriatrics Society",
        "International journal of environmental research and public health": "International Journal of Environmental Research and Public Health",
        "Annual review of public health": "Annual Review of Public Health", "Perspectives on psychological science : a journal of the Association for Psychological Science": "Perspectives on Psychological Science",
        "Osong public health and research perspectives": "Osong Public Health and Research Perspectives", "World journal of emergency surgery : WJES": "World Journal of Emergency Surgery",
        "Archives of academic emergency medicine": "Archives of Academic Emergency Medicine", "Clinical and experimental emergency medicine": "Clinical and Experimental Emergency Medicine",
        "The American journal of emergency medicine": "The American Journal of Emergency Medicine", "Asia-Pacific journal of public health": "Asia-Pacific Journal of Public Health",
        "Journal of epidemiology and community health": "Journal of Epidemiology and Community Health", "International journal of epidemiology": "International Journal of Epidemiology",
        "International journal of injury control and safety promotion": "International Journal of Injury Control and Safety Promotion", "Epidemiology (Cambridge, Mass.)": "Epidemiology",
        "Journal of Korean medical science": "Journal of Korean Medical Science", "Health & place": "Health & Place", "Injury epidemiology": "Injury Epidemiology", "Biometrics": "Biometrics"}
def jname(k):
    r = REFS[k]; j = r.get("journal_full") or r.get("journal", "")
    if j in JFIX: return JFIX[j]
    j = re.sub(r"\s*\([^)]*\)\s*$", "", j).split(" : ")[0].replace(";", "")
    ws = j.split(" "); return " ".join(w if (w.isupper() or (i and w.lower() in SMALL)) else (w[:1].upper() + w[1:]) for i, w in enumerate(ws))
def person(a):
    p = a.split(" "); ini = p[-1]
    if len(p) >= 2 and ini.isupper() and ini.isalpha() and len(ini) <= 4: return " ".join(p[:-1]), " ".join(c + "." for c in ini)
    return a, ""
def surnames(k):
    au = REFS[k]["authors"]
    return [au] if isinstance(au, str) else [person(a)[0] for a in au]
def base_label(k):
    s = surnames(k); return (s[0] if len(s) == 1 else f"{s[0]} and {s[1]}" if len(s) == 2 else f"{s[0]} et al."), REFS[k]["year"]
_lab = {}
for k in KEYS: _lab.setdefault(base_label(k), []).append(k)
SUFFIX = {}; LAB2 = {}
for (_a, _y), ks in _lab.items():
    if len(ks) > 1:
        if len({surnames(k)[0] for k in ks}) == 1 and len({tuple(surnames(k)[:2]) for k in ks}) == len(ks):
            for k in ks: s_ = surnames(k); LAB2[k] = f"{s_[0]}, {s_[1]}, et al." if len(s_) > 2 else f"{s_[0]} and {s_[1]}"
        else:
            for i, k in enumerate(sorted(ks, key=lambda x: REFS[x]["title"].lower())): SUFFIX[k] = "abcdefgh"[i]
def year(k): return f"{REFS[k]['year']}{SUFFIX.get(k, '')}"
def aylabel(k):
    a = LAB2.get(k) or base_label(k)[0]; return ((a.lower(), year(k)), f"{a}, {year(k)}")
def ini(i): return i.replace(" ", "")
def apa_authors(k):
    au = REFS[k]["authors"]
    if isinstance(au, str): return au
    return ", ".join(f"{s}, {ini(i)}" if i else s for s, i in (person(a) for a in au))
def full_pages(p):
    m = re.fullmatch(r"([A-Za-z]?)(\d+)-([A-Za-z]?)(\d+)", p or "")
    if not m: return p
    a, b = m.group(2), m.group(4)
    if len(b) < len(a): b = a[:len(a) - len(b)] + b
    return f"{m.group(1)}{a}-{m.group(3)}{b}"
JAB = {"Annals of the Institute of Statistical Mathematics": "Ann. Inst. Stat. Math.", "Annual review of public health": "Annu. Rev. Public Health", "Annual Review of Public Health": "Annu. Rev. Public Health",
       "Journal of the Royal Statistical Society Series B: Statistical Methodology": "J. R. Stat. Soc. Ser. B Stat. Methodol.", "Statistical Science": "Stat. Sci.",
       "Statistical methods in medical research": "Stat. Methods Med. Res.", "Statistics in medicine": "Stat. Med.", "Asia Pac J Public Health": "Asia Pac. J. Public Health"}
def jabbr(k):
    r = REFS[k]
    if (r.get("journal") or "") in JAB: return JAB[r["journal"]]
    a = r.get("journal") or jname(k); full = {w.strip(",;:.()").lower() for w in (r.get("journal_full") or jname(k)).replace("&", " ").replace("-", " ").split()}
    out = []
    for w in a.split():
        lw = w.lower().strip(".")
        out.append(w if (lw in full or (w.isupper() and len(w) > 1) or w.endswith(".")) else w + ".")
    return " ".join(out)
def aref(k):
    r = REFS[k]; A = apa_authors(k)
    if r["type"] == "web": return f"{A}, {year(k)}. {r['title']}. {r['url']} (accessed {r.get('accessed', '')})."
    if r["type"] == "book": return f"{A}, {year(k)}. {sent(r['title'])}. {r.get('publisher', '')}." + (f" https://doi.org/{r['doi']}." if r.get("doi") else "")
    t = sent(r["title"].rstrip(".")); t = t + ("" if t.endswith(("?", "!")) else ".")
    s = f"{A}, {year(k)}. {t} {jabbr(k)}"
    if r.get("vol"): s += f" {r['vol']}" + (f", {full_pages(r['pages']).replace('-', chr(8211))}" if r.get("pages") else "")
    return s + "." + (f" https://doi.org/{r['doi']}." if r.get("doi") else "")
def sortkey(k):
    au = REFS[k]["authors"]; s = [(au.lower(), "")] if isinstance(au, str) else [(person(a)[0].lower(), person(a)[1].lower()) for a in au]
    return (s, year(k))

class TX(JKMS):
    raw = False; table_bold = True
    def aylabel(self, k): return aylabel(k)
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw: text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text)
        return super()._emit(p, text, sz, bold, italic)

import tables_elti as BT

def title_page():
    J = TX(cite="ay")
    J.para(f"<b>{TITLE}</b>")
    J.para("Seongdae Kim", before=8); J.para(f"ORCID: https://orcid.org/{ORCID}")
    J.para(AFFIL, before=6)
    J.para(f"<b>Corresponding author:</b> Seongdae Kim, {AFFIL}. Email: {EMAIL}. Phone: {PHONE}.", before=8)
    J.para(f"<b>Acknowledgements:</b> {ACK}", before=8)
    J.para(f"<b>Declaration of interest:</b> {COI}", before=6)
    J.para(f"<b>Funding:</b> {FUNDING}", before=6)
    J.para(f"<b>Ethics:</b> {IRB_FULL}", before=6)
    J.para(f"<b>Data availability:</b> {data_full()}", before=6)
    J.para(f"<b>CRediT authorship contribution statement:</b> {CREDIT}", before=6)
    J.para(f"<b>{AI_HEAD}:</b> {AI_STATEMENT}", before=6)
    return J

def build(bw=0, aw=0):
    D = read_draft(); J = TX(cite="ay")
    J.para(f"<b>{TITLE}</b>")
    J.para(f"<b>Word count:</b> {bw} (main text, excluding abstract, tables, figure captions and references); abstract {aw}. <b>Tables:</b> 2. <b>Figures:</b> 3. <b>References:</b> {len(KEYS)}.", before=6)
    J.page_break(); J.head("Abstract", 1)
    for p in D["Abstract"]: J.para(p)
    J.para(f"<b>Keywords:</b> {'; '.join(C.KEYWORDS)}", before=6)
    J.page_break(); J.counting = True
    J.head("1. Introduction", 1)
    for p in D["Introduction"]: J.para(cites(p), indent=True)
    J.head("2. Materials and methods", 1)
    for i, x in enumerate(C.METHODS, 1):
        J.head(f"2.{i}. {x[0]}", 2)
        for p in x[1:]: J.para(cites(p.replace("IRB_SENTENCE", IRB_ANON)), indent=True)
    J.head("3. Results", 1)
    for i, x in enumerate(C.RESULTS, 1):
        J.head(f"3.{i}. {x[0]}", 2)
        for p in x[1:]:
            if p.startswith("@@"): BT.place(J, p[2:], N); continue
            J.para(cites(p), indent=True)
    J.head("4. Discussion", 1)
    for p in D["Discussion"]:
        if p.startswith("### "): J.head(p[4:].strip(), 2); continue
        J.para(cites(p), indent=True)
    J.head("5. Implications for policy and practice", 1)
    for p in D["Implications for policy and practice"]: J.para(cites(p), indent=True)
    J.head("6. Conclusions", 1)
    for p in D["Conclusions"]: J.para(cites(p), indent=True)
    J.counting = False
    J.head("Data availability", 1); J.para(DATA_ANON)
    J.head(AI_HEAD, 1); J.para(AI_STATEMENT)
    assert sorted(set(J.cites)) == KEYS, (set(J.cites) ^ set(KEYS))
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for k in sorted(KEYS, key=sortkey): s = aref(k); rl.append(s); J.para(s, hang=True) if "hang" in J.para.__code__.co_varnames else J.para(s)
    J.raw = False
    return J, rl, D

def docx_bw(path):
    from docx import Document
    t = "\n".join(x.text for x in Document(path).paragraphs)
    i = t.find("\n1. Introduction\n"); j = t.find("\nData availability\n"); assert 0 < i < j; return len(t[i:j].split())

if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript_anonymized.docx"); D = read_draft()
    aw = sum(len(x.split()) for x in D["Abstract"])
    J, rl, D = build(); J.doc_title = ""; J.save(p); bw = docx_bw(p)
    J, rl, D = build(bw, aw); J.doc_title = ""; J.save(p); assert docx_bw(p) == bw
    T = title_page(); T.doc_title = ""; T.save(os.path.join(OUT, "Title_page.docx"))
    for f in ("Manuscript_anonymized.docx", "Title_page.docx"):
        subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_elti", "--convert-to", "pdf", "--outdir", OUT, os.path.join(OUT, f)], check=True, capture_output=True)
    open(os.path.join(OUT, "wordcount.txt"), "w").write(f"body_words={bw}\nabstract_words={aw}\nrefs={len(KEYS)}\ntables=2\nfigures=3\n")
    open(os.path.join(OUT, "reference_list.txt"), "w").write("\n".join(rl) + "\n")
    print(f"body {bw} | abstract {aw} | refs {len(KEYS)}"); assert aw <= 250, aw; assert 3000 <= bw <= 6000, bw
