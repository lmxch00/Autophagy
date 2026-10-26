# -*- coding: utf-8 -*-
"""生成公开发布版语料：剔除出版商版权摘要，保留可复现所需的全部元数据

理由：PubMed / Europe PMC 的摘要（abstract）受出版商版权约束，批量再分发到公开仓库
存在合规风险；而题录（PMID/PMCID/DOI/题名/年份/刊名）足以完整定义语料，且检索式已逐字
公开、任何人可自行重跑检索复现全部计数。
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "corpus_clean.json")
dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "corpus_public.json")

d = json.load(open(src, encoding="utf-8"))
KEEP = ["pmid", "pmcid", "doi", "title", "year", "journal", "pubType"]
out = {
    "query": d["query"],
    "retrieved_at": d.get("retrieved_at"),
    "hitCount": d.get("hitCount"),
    "n": d.get("n"),
    "note": ("Abstracts removed from this public copy: they are publisher-copyrighted text "
             "obtained via Europe PMC and are not redistributed here. The corpus is fully "
             "defined by the query above and by the bibliographic fields retained per record."),
    "records": [{k: r.get(k) for k in KEEP} for r in d["records"]],
}
json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

n_abs = sum(1 for r in d["records"] if r.get("abstract"))
print(f"写出 {dst}")
print(f"记录 {len(out['records'])} 条｜剔除摘要 {n_abs} 条｜体积 {os.path.getsize(src)} → {os.path.getsize(dst)} B")
