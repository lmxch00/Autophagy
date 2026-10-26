# -*- coding: utf-8 -*-
"""A31 硬锚点（定稿版）：语料重建 + 三维编码
语料定义（可复算，逐字）：
  SRC:MED 且题名自述 "autophagy-related" 且题名含 prognostic|signature|risk score|risk model|
  risk signature|risk stratification，发表日 2021-01-01 至 2026-10-26，排除 PUB_TYPE:"review"
  —— 即"以转录组衍生的自噬相关评分/签名作为主要产出"的原始研究全集
编码三维：
  E1 证据层 wetlab  = 正文出现 (western blot|IHC|IF|TEM) 且出现自噬读数 (LC3/SQSTM1/p62/ATG/autophagosom)
  E2 证据层 flux    = 阻断剂(bafilomycin/BafA1/concanamycin/ammonium chloride/CQ) 与 LC3-II/flux/accumulat 同句，或串联探针
  C1 主张层         = 同一句内把"评分/分组"与"自噬活性/水平"绑定的解释句（全部留存供人读）
污染守卫：正文含 "Reviewer #" / "peer review" 标记者标记 suspected_review_file
"""
import json, os, re, time, concurrent.futures as cf, urllib.request, urllib.parse

OUT = os.path.dirname(os.path.abspath(__file__))
API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
FT = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"

QUERY = ('SRC:MED AND (TITLE:"autophagy-related" OR TITLE:"autophagy related") '
         'AND (TITLE:prognostic OR TITLE:signature OR TITLE:"risk score" OR TITLE:"risk model" '
         'OR TITLE:"risk signature" OR TITLE:"risk stratification") '
         'AND (FIRST_PDATE:[2021-01-01 TO 2026-10-26]) NOT PUB_TYPE:"review"')

def jget(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "A31-audit/2.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            time.sleep(2 + 2 * i)
    return None

def fetch_corpus():
    recs, cursor, total = [], "*", None
    while True:
        u = API + "?" + urllib.parse.urlencode({"query": QUERY, "format": "json", "pageSize": 1000,
                                                "resultType": "core", "cursorMark": cursor})
        d = jget(u)
        if not d:
            break
        total = d.get("hitCount")
        b = d.get("resultList", {}).get("result", [])
        recs.extend(b)
        nc = d.get("nextCursorMark")
        if not nc or nc == cursor or not b:
            break
        cursor = nc
    seen, uniq = set(), []
    for r in recs:
        k = r.get("pmid") or r.get("id")
        if k in seen:
            continue
        seen.add(k); uniq.append(r)
    slims = []
    for r in uniq:
        ji = r.get("journalInfo", {}) or {}
        slims.append({
            "pmid": r.get("pmid"), "pmcid": r.get("pmcid"), "doi": r.get("doi"),
            "title": r.get("title"), "year": r.get("pubYear"),
            "journal": (ji.get("journal", {}) or {}).get("medlineAbbreviation")
                        or (ji.get("journal", {}) or {}).get("title"),
            "pubType": r.get("pubTypeList", {}).get("pubType"),
            "abstract": (r.get("abstractText") or "")[:6000],
        })
    json.dump({"query": QUERY, "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
               "hitCount": total, "n": len(slims), "records": slims},
              open(os.path.join(OUT, "corpus_clean.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"语料 {total} § 去重 {len(slims)}｜有 PMCID {sum(1 for s in slims if s['pmcid'])}", flush=True)
    return slims

BLOCK = re.compile(r"bafilomycin|baf[\s\-]?a1|concanamycin|ammonium chloride|chloroquine|\bCQ\b", re.I)
LCDEG = re.compile(r"LC3[\s\-]?II|LC3B[\s\-]?II|flux|accumulat|turnover|degradation", re.I)
TANDEM = re.compile(r"RFP[\s\-]?GFP[\s\-]?LC3|GFP[\s\-]?RFP[\s\-]?LC3|tfLC3|tandem[\s\-]?(fluorescent|fluorescence)[\s\-]?LC3|mCherry[\s\-]?GFP[\s\-]?LC3|mRFP[\s\-]?GFP[\s\-]?LC3|Keima", re.I)
WB = re.compile(r"western\s*blot|immunoblot", re.I)
IH = re.compile(r"immunohistochem|immunocyto|immunofluoresc|fluorescence\s+microscop|confocal", re.I)
TEM = re.compile(r"transmission\s+electron\s+microscop|\bTEM\b", re.I)
READOUT = re.compile(r"\bLC3(?:B|A)?\b|MAP1LC3B|SQSTM1|\bp62\b|\bATG\d+\b|autophagosom", re.I)
ACT = re.compile(r"autophag\w*\s+(?:activity|level|levels|flux|status|capacity|efficiency)|"
                 r"(?:enhanc|increas|activat|induc|suppress|impair|inhibit|reduc)\w*\s+(?:the\s+)?autophag\w*", re.I)
ANCHOR = re.compile(r"risk\s+score|high[\s\-]risk|low[\s\-]risk|risk\s+group|signature|score|subtype|cluster", re.I)

def getft(pmcid, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(FT.format(pmcid=pmcid), headers={"User-Agent": "A31-audit/2.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception:
            time.sleep(1.5 + 1.5 * i)
    return None

def clean(xml):
    t = re.sub(r"<[^>]+>", " ", xml)
    return re.sub(r"\s+", " ", re.sub(r"&[a-z]+;", " ", t))

def work(rec):
    xml = getft(rec["pmcid"])
    if not xml or len(xml) < 2000:
        return {"pmcid": rec["pmcid"], "pmid": rec["pmid"], "ok": False}
    txt = clean(xml)
    sents = [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", txt) if len(s) < 700]
    flux_snip = [s for s in sents if BLOCK.search(s) and LCDEG.search(s)]
    claims = [s for s in sents if ACT.search(s) and ANCHOR.search(s)][:6]
    return {
        "pmcid": rec["pmcid"], "pmid": rec["pmid"], "year": rec["year"],
        "journal": rec["journal"], "title": rec["title"], "ok": True,
        "review_file": bool(re.search(r"Reviewer\s*#|peer\s+review\s+file|Reviewer report", txt, re.I)),
        "wetlab": bool((WB.search(txt) or IH.search(txt) or TEM.search(txt)) and READOUT.search(txt)),
        "flux": bool(flux_snip) or bool(TANDEM.search(txt)),
        "tandem": bool(TANDEM.search(txt)),
        "n_claim": len(claims), "claims": claims,
        "flux_snip": flux_snip[:3],
    }

def main():
    slims = fetch_corpus()
    recs = [r for r in slims if r.get("pmcid")]
    res, done = [], 0
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        for r in ex.map(work, recs):
            res.append(r); done += 1
            if done % 25 == 0:
                print(f"  {done}/{len(recs)}", flush=True)
    json.dump({"generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "query": QUERY, "records": res},
              open(os.path.join(OUT, "coding_clean.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    ok = [r for r in res if r.get("ok") and not r["review_file"]]
    n = len(ok)
    print(f"\n可编码 {len([r for r in res if r.get('ok')])}｜剔评审档案后 {n}")
    print(f"E1 有湿实验自噬读数 : {sum(r['wetlab'] for r in ok)} = {100*sum(r['wetlab'] for r in ok)/n:.1f}%")
    print(f"E2 有通量证据       : {sum(r['flux'] for r in ok)} = {100*sum(r['flux'] for r in ok)/n:.1f}%")
    print(f"   其中串联探针     : {sum(r['tandem'] for r in ok)}")
    print(f"C1 有'评分=自噬活性'解释句: {sum(1 for r in ok if r['n_claim']>0)} = {100*sum(1 for r in ok if r['n_claim']>0)/n:.1f}%")
    print(f"纯计算(无湿实验)    : {sum(1 for r in ok if not r['wetlab'])} = {100*sum(1 for r in ok if not r['wetlab'])/n:.1f}%")

if __name__ == "__main__":
    main()
