# -*- coding: utf-8 -*-
"""A31 硬化：句级复核（替换文档级共现）
tier2 要求：同一句内同时出现 方法(WB/IHC/IF/EM) 与 自噬标志物(LC3/SQSTM1/p62/ATG*)
否则降为 tier1；flux 判定沿用句级（已是句级）
"""
import json, os, re, time, urllib.request, concurrent.futures as cf

OUT = os.path.dirname(os.path.abspath(__file__))
FT = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"

METHOD = re.compile(r"western\s*blot|immunoblot|immunohistochem|immunocyto|immunofluoresc|"
                    r"fluorescence\s+microscop|confocal|electron\s+microscop", re.I)
MARKER = re.compile(r"\bLC3(?:B|A)?(?:[\s\-]?I{1,2})?\b|MAP1LC3B|SQSTM1|\bp62\b|\bATG\d+\b|autophagosom", re.I)
BLOCK = re.compile(r"bafilomycin|baf[\s\-]?a1|concanamycin|ammonium chloride|chloroquine|\bCQ\b", re.I)
LCDEG = re.compile(r"LC3[\s\-]?II|LC3B[\s\-]?II|flux|accumulat|turnover|degradation", re.I)
TANDEM = re.compile(r"RFP[\s\-]?GFP[\s\-]?LC3|GFP[\s\-]?RFP[\s\-]?LC3|tfLC3|tandem[\s\-]?(fluorescent|fluorescence)[\s\-]?LC3|mCherry[\s\-]?GFP[\s\-]?LC3|mRFP[\s\-]?GFP[\s\-]?LC3|Keima", re.I)

def getft(p, tries=3):
    for i in range(tries):
        try:
            r = urllib.request.Request(FT.format(pmcid=p), headers={"User-Agent": "A31-audit/3.0"})
            with urllib.request.urlopen(r, timeout=90) as h:
                return h.read().decode("utf-8", "ignore")
        except Exception:
            time.sleep(1.5 + 1.5 * i)
    return None

def work(rec):
    xml = getft(rec["pmcid"])
    if not xml or len(xml) < 2000:
        return {"pmcid": rec["pmcid"], "ok": False}
    t = re.sub(r"\s+", " ", re.sub(r"&[a-z]+;", " ", re.sub(r"<[^>]+>", " ", xml)))
    sents = [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", t) if len(s) < 700]
    method_marker_sent = [s for s in sents if METHOD.search(s) and MARKER.search(s)]
    flux_sent = [s for s in sents if BLOCK.search(s) and LCDEG.search(s)]
    return {"pmcid": rec["pmcid"], "pmid": rec["pmid"], "year": rec["year"],
            "journal": rec["journal"], "title": rec["title"], "ok": True,
            "review_file": bool(re.search(r"Reviewer\s*#|peer\s+review\s+file|Reviewer report", t, re.I)),
            "tier2_sentlevel": bool(method_marker_sent),
            "flux": bool(flux_sent) or bool(TANDEM.search(t)),
            "tandem": bool(TANDEM.search(t)),
            "mm_snip": method_marker_sent[:1], "flux_snip": flux_sent[:1]}

def main():
    d = json.load(open(os.path.join(OUT, "coding_clean.json"), encoding="utf-8"))
    recs = [r for r in d["records"] if r.get("ok") and not r["review_file"]]
    res = []
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        for i, r in enumerate(ex.map(work, recs), 1):
            res.append(r)
            if i % 25 == 0:
                print(f"  {i}/{len(recs)}", flush=True)
    ok = [r for r in res if r.get("ok")]
    json.dump({"generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "records": ok},
              open(os.path.join(OUT, "coding_sentlevel.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    n = len(ok)
    t2 = [r for r in ok if r["tier2_sentlevel"]]
    fl = [r for r in t2 if r["flux"]]
    t1 = n - len(t2)
    print(f"\n可编码 {n}")
    print(f"tier1 无湿实验(句级) : {t1} ({100*t1/n:.1f}%)")
    print(f"tier2 静态标志物(句级): {len(t2)-len(fl)} ({100*(len(t2)-len(fl))/n:.1f}%)")
    print(f"tier3 通量判别        : {len(fl)} ({100*len(fl)/n:.1f}%)")
    print(f"湿实验合计 {len(t2)}｜其中通量 {len(fl)} ({100*len(fl)/max(1,len(t2)):.1f}%)")
    # 与文档级对比
    doc_level = [r for r in recs if r["wetlab"]]
    print(f"[对照] 文档级湿实验 {len(doc_level)}｜句级 {len(t2)}｜降级 {len(doc_level)-len(t2)}")

if __name__ == "__main__":
    main()
