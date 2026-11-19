# build_refs_elti.py — ELTI 참고문헌 메타데이터 캐시(refs_elti.json, 2026-11-19). 키 = 원고 원천(draft md + content_elti.py)의 [@key].
#  방법·교통 문헌은 이미 PubMed·Crossref로 검증된 이전 호 캐시(TRANS 우선, 그다음 로컬 refs_*.json)에서 복사, 새 주제 문헌은 manifest(ALL_refs.csv) PMID → PubMed esummary. 네트워크는 이 스크립트에서만.
import os, re, json, time, glob, urllib.request
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); AN = os.path.dirname(os.path.dirname(MS))
src = open(os.path.join(HERE, "content_elti.py"), encoding="utf-8").read() + open(os.path.join(MS, "draft", "01_manuscript.md"), encoding="utf-8").read()
src = re.sub(r"<!--.*?-->", "", src, flags=re.S); src = re.sub(r"(?m)^\s*#.*$", "", src)
keys = sorted({k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")}); keys = [k for k in keys if re.fullmatch(r"(web:)?[a-z][a-z0-9]*", k)]
OLD = {}
for f in [os.path.join(HERE, "_refs_trans_src.json")] + sorted(glob.glob(os.path.join(AN, "*", "MS*", "build", "refs_*.json"))):
    if "ELTI" in f: continue
    try:
        if "dataless" in os.popen(f"stat -f %Sf '{f}'").read(): continue
        for k, v in json.load(open(f, encoding="utf-8")).items(): OLD.setdefault(k, v)
    except Exception: pass
OLD["web:kosis2026elderly"] = dict(type="web", authors="Statistics Korea", title="e-Local indicators: road traffic crashes involving older people (crashes, deaths and injured persons) by province, city, county and district, and population aged 65 years or older by district, 2011–2025 (source: Korean National Police Agency; Ministry of the Interior and Safety). Korean Statistical Information Service", url="https://kosis.kr", year=2026, accessed="19 November 2026")
OLD["web:kosis2026road"] = dict(type="web", authors="Statistics Korea", title="e-Local indicators: registered motor vehicles per resident, drink-driving crashes, all road traffic crashes, road pavement and traffic culture index by district, 2011–2024. Korean Statistical Information Service", url="https://kosis.kr", year=2026, accessed="19 November 2026")
M = pd.read_csv(os.path.join(MS, "refs", "manifest", "ALL_refs.csv"), dtype=str).fillna("").set_index("key")
pm = [k for k in keys if k not in OLD]
miss = [k for k in pm if k not in M.index or not M.loc[k, "pmid"]]; assert not miss, miss
out = {}
if pm:
    d = json.load(urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(M.loc[k, "pmid"] for k in pm), timeout=60))["result"]
    for k in pm:
        r = d[M.loc[k, "pmid"]]
        au = [a["name"] for a in r["authors"] if a.get("authtype", "Author") == "Author"] or [a["name"] for a in r["authors"]]
        doi = next((a["value"] for a in r["articleids"] if a["idtype"] == "doi"), "") or M.loc[k, "doi"]
        out[k] = dict(type="journal", authors=au, title=r["title"].rstrip("."), journal=r["source"].replace(".", ""), year=int(r["pubdate"][:4]), vol=r.get("volume", ""), issue=r.get("issue", ""), pages=r.get("pages", ""), doi=doi, pmid=M.loc[k, "pmid"], verified="PubMed esummary " + time.strftime("%Y-%m-%d"))
for k in keys:
    if k in OLD: out[k] = OLD[k]
def fullp(p):
    m = re.match(r"^(\d+)-(\d+)$", str(p))
    if not m: return p
    a, b = m.groups(); return p if len(b) >= len(a) else f"{a}-{a[:len(a)-len(b)]+b}"
for k, v in out.items():
    if v.get("type") == "journal": v["pages"] = fullp(v.get("pages", "")); v["authors"] = [a.title() if a.isupper() else a for a in v["authors"]]
json.dump(out, open(os.path.join(HERE, "refs_elti.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(keys), "keys;", len(pm), "from PubMed;", "MISSING", [k for k in keys if k not in out])
for k in keys: v = out[k]; print(k, "|", v.get("journal"), v.get("year"), v.get("vol"), v.get("pages"), "|", str(v.get("title"))[:70])
# ── APA: 학술지 전체 이름(fulljournalname)·전자 논문 번호(elocationid) 보충(2026-11-19) ──
out = json.load(open(os.path.join(HERE, "refs_elti.json"), encoding="utf-8"))
pm2 = {k: v["pmid"] for k, v in out.items() if v.get("type") == "journal" and v.get("pmid")}
d = json.load(urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(pm2.values()), timeout=60))["result"]
for k, p in pm2.items():
    r = d[p]; out[k]["journal_full"] = r.get("fulljournalname", "")
    if not out[k].get("pages"):
        el = r.get("elocationid", ""); m = re.search(r"pii:\s*(\S+)", el)
        if m: out[k]["pages"] = m.group(1).rstrip(".")
FIXP = {"park2020exploring": "2358", "western2025senior": "afaf345"}   # Crossref page·article-number(2026-11-19)
for k, v in FIXP.items(): out[k]["pages"] = v
JFN = {"bell2015explaining": "Political Science Research and Methods", "gelman2014understanding": "Statistics and Computing"}
for k, v in JFN.items():
    if k in out: out[k]["journal_full"] = v
json.dump(out, open(os.path.join(HERE, "refs_elti.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("no pmid:", [(k, v.get("journal")) for k, v in out.items() if v.get("type") == "journal" and not v.get("pmid")])
print("no pages:", [k for k, v in out.items() if v.get("type") == "journal" and not v.get("pages")])
