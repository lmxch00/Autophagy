# A31 — Data and code archive / 数据与代码归档

**Correspondence / 对应稿件**
Autophagy-related prognostic signatures report gene expression, not autophagic flux: 169 coded reports from a census of 212

**Repository / 仓库**: https://github.com/lmxch00/Autophagy (public, published 26 October 2026) · **Archived copy / 归档副本**: https://doi.org/10.17605/OSF.IO/9SRG3 (OSF, 26 October 2026)
**Target journal / 目标期刊**: Autophagy (Taylor & Francis)
**Version / 版本**: v2, 2026-10-26
**Author · contact / 作者 · 联系方式**: Bing Zhang, Department of Oncology, Tangshan People's Hospital, Tangshan, Hebei, China · yanjiu12@126.com · ORCID 0000-0003-1062-4207

---

## 1 Purpose / 用途

**EN** — This archive accompanies the Letter to the Editor named above. It holds the search output, the sentence-level coding, and the scripts that generate every count reported in Table 1 and in the text, so that each figure can be recomputed rather than taken on trust.

**中文** — 本归档对应上述致编辑信。内含检索输出、句级编码与生成脚本；正文与表 1 的每一个数字都可由本包复算，而不必依赖作者陈述。

---

## 2 Contents / 内容

| File / 文件 | Content / 内容 |
|---|---|
| `corpus_clean.json` | The 212 eligible records as returned by the search (PMID, PMCID, DOI, title, year, journal, publication type). **Abstracts are deliberately not included** — see §3. / 检索返回的 212 条合格记录（PMID、PMCID、DOI、题名、年份、刊名、文献类型）。**摘要已刻意不含**，见 §3。 |
| `coding_clean.json` | Per-record coding: presence of a wet-laboratory readout, presence of a flux-discriminating experiment, and the sentence used for the 15 reports that call the score a measure of autophagy activity. / 逐条编码：是否含湿实验读数、是否含通量判别实验，以及 15 篇"自报测度"的判定句。 |
| `coding_sentlevel.json` | Per-record results of the sentence-level pass (strict rule) together with every matched sentence. / 句级复核（严格规则）的逐条结果与全部命中句。 |
| `_audit_clean.py` | Search and coding script, including the query. / 检索与编码脚本（含检索式）。 |
| `_audit_sentlevel.py` | Sentence-level re-coding script. / 句级复核脚本。 |
| `make_public_release.py` | Regenerates the published corpus from the full local file by removing the abstracts. / 由本地完整文件生成公开版语料（剔除摘要）。 |
| `LICENSE` | The licence of this archive: **CC BY 4.0**. / 本归档的许可协议：CC BY 4.0。 |
| `CITATION.cff` | Citation metadata for GitHub and Zenodo. / GitHub 与 Zenodo 读取的引文元数据。 |
| `README.md` | This file. / 本文件。 |

**Quoted text / 引文说明**: the two coding files contain short quoted sentences (about 11,000 characters in total, each attached to the PMID of the source report) as the evidence for every tier assignment. These are citations of the kind normally used in critical commentary.

**EN** — `coding_clean.json` and `coding_sentlevel.json` carry short quoted sentences (about 11,000 characters in total, each tied to the PMID of the source report) as the evidence behind every tier assignment.

**中文** — 两个编码文件内含短引句（合计约 11,000 字符，每条均附来源 PMID），作为每项分层判定的证据。

---

## 3 Why the abstracts are not here / 为什么不含摘要

**EN** — The abstracts obtained from PubMed and Europe PMC are publisher-copyrighted text. Republishing them in bulk inside a public repository is a rights problem, and it is not necessary: the corpus is fully defined by the query below together with the bibliographic fields retained per record, and anyone can re-run the search to obtain the same 212 reports. The full local file, with abstracts, is retained by the author and can be supplied on request.

**中文** — 自 PubMed 与 Europe PMC 取得的摘要属出版商版权文本，将其批量再分发至公开仓库存在权利风险，且并无必要：语料由下方检索式与每条记录保留的题录字段完全界定，任何人都可重跑检索得到同样的 212 篇。含摘要的完整本地文件由作者保留，可按请求提供。

---

## 4 Reproduction / 复现

**EN** — Run `_audit_clean.py` first (about 2 minutes; it retrieves the full text of 180 reports), then `_audit_sentlevel.py` (about 1 minute). Both write their output next to the scripts. `_audit_clean.py` regenerates `corpus_clean.json` **with** abstracts; run `make_public_release.py` afterwards to return the published copy to its abstract-free form.

**中文** — 先运行 `_audit_clean.py`（约 2 分钟，会取 180 篇全文），再运行 `_audit_sentlevel.py`（约 1 分钟），两者均将结果写在脚本同目录。`_audit_clean.py` 生成的 `corpus_clean.json` **含**摘要；随后运行 `make_public_release.py` 即可还原为不含摘要的公开版。

**Query used / 所用检索式** (Europe PMC, run 26 October 2026):

```
SRC:MED AND (TITLE:"autophagy-related" OR TITLE:"autophagy related")
AND (TITLE:prognostic OR TITLE:signature OR TITLE:"risk score" OR TITLE:"risk model"
     OR TITLE:"risk signature" OR TITLE:"risk stratification")
AND (FIRST_PDATE:[2021-01-01 TO 2026-10-26]) NOT PUB_TYPE:"review"
```

---

## 5 Environment / 运行环境

**EN** — Python 3.9 or later (tested on 3.13). Standard library only: no third-party packages are required. Network access to the Europe PMC REST service is required.

**中文** — Python 3.9 及以上（实测 3.13）。仅使用标准库，无需安装任何第三方包。需可访问 Europe PMC REST 服务。

---

## 6 What the numbers mean / 计数口径

**EN** — 212 records were eligible; full text was available for 180; 169 were coded. Reports were placed in three tiers: no autophagy marker measured at the protein or ultrastructural level; marker measured but without a lysosomal inhibitor or tandem reporter, so direction cannot be inferred; and flux-discriminating. Each report was coded twice, once requiring the marker and the method to share a sentence (strict) and once requiring only that they occur in the same document (permissive). The flux tier is identical under both rules, which is why the Letter's conclusion does not depend on how strictly the text was read.

**中文** — 合格记录 212 条；取得全文 180 条；完成编码 169 条。按测量内容分三层：未在蛋白或超微结构层面测量任何自噬标志物；测量了标志物但未做溶酶体抑制或串联报告子，因而无法判定方向；可辨别通量方向。每条记录编码两次：严格规则要求标志物与方法同句，宽松规则只要求同文档出现。两套规则下"通量判别"一层完全一致，故信件的结论不依赖读稿的严格程度。

---

## 7 Known limitations / 已知限制

**EN**

1. All coding was performed by a single coder. No second coder was available, so no inter-coder coefficient is reported; what is offered instead is the agreement between the two coding rules and the manual reading of every candidate sentence in the flux tier.
2. Full text was obtainable only for the 180 reports that Europe PMC serves. The 32 without full text are not a random subset; the direction this loss is likely to take is stated in the Letter.
3. A readout described only in a supplementary file would be missed. That error moves reports from the first tier into the second and leaves the flux count unchanged.

**中文**

1. 全部编码由单一编码者完成，无第二编码者，故未报编码者间系数；替代给出的是两套编码规则之间的一致性与通量层每一句的人工阅读结果。
2. 仅 Europe PMC 可提供的 180 篇取得了全文。无全文的 32 篇并非随机缺失，该损耗的可能方向已在信中说明。
3. 仅见于补充材料的读数会被漏检。该误差会把报告从第一层移入第二层，但不改变通量层的计数。

---

## 8 Publication status / 发布状态

**EN** — The GitHub repository went live on 26 October 2026 at https://github.com/lmxch00/Autophagy (public, default branch `main`). It contains the nine files listed in §2 and nothing else; each uploaded file was verified against the local copy by Git blob SHA-1, so the published bytes are the reviewed bytes.

**中文** — GitHub 仓库已于 2026 年 10 月 26 日上线于 https://github.com/lmxch00/Autophagy（公开仓，默认分支 `main`）。仓库仅含 §2 所列九个文件，无其他内容；每个上传文件均以 Git blob SHA-1 与本地副本逐字节比对一致，即线上即所审。

**Canonical version / 规范版本** — this file is the canonical description of the archive. The copy held in the OSF project may be one revision behind it; the GitHub repository and this file are updated together, and the per-file SHA-256 values in the OSF record are what identifies the archived bytes.

**Second archive / 第二处归档** — Zenodo, the usual route for archiving a GitHub repository with a DOI, was not reachable from this network (`http=000` on 26 October 2026), so the DOI was minted on **OSF** instead. The nine files are deposited there individually, and each was verified byte-for-byte against this repository by SHA-256 on 26 October 2026: https://doi.org/10.17605/OSF.IO/9SRG3

The OSF record is the citable one; this repository remains the live, browsable copy.

**Still open / 尚待完成**

1. **Institutional mirror / 机构镜像** — the repository is held on a personal account. Archiving a copy in an institutional or national repository makes the data durable if the account is withdrawn, and is what reviewers sometimes ask for with personal-account deposits.
2. **Zenodo, later / 日后再谈 Zenodo** — worth adding a second copy when a network with access to Zenodo is available, so that the DOI resolves from more contexts.
3. **OSF housekeeping / OSF 收尾**: the OSF project licence is set to **CC BY 4.0**, the project Description carries the DOI and the GitHub link, the project Wiki page "Home" carries this bilingual description, and all nine archived files match this repository byte-for-byte by SHA-256. (OSF does not expose a per-file licence field; the archive licence is recorded at project level and stated in §9. If you are reading an earlier copy of this file, take the current one from the GitHub repository, which is the canonical location.)

**中文** — **OSF 收尾**：OSF 项目许可为 **CC BY 4.0**，Description 含 DOI 与 GitHub 链接，项目 Wiki 的 "Home" 页载有本双语说明，九个归档文件与本仓库逐字节一致。（OSF 不提供文件级许可字段，归档许可记录在项目级，见 §9。若你读的是本文件的较早版本，请以 GitHub 仓库为准——那里是规范位置。）

## 9 Licence / 许可

**EN** — This archive is released under **CC BY 4.0** (see the `LICENSE` file). Attribution is required; no additional restrictions apply.

**中文** — 本归档以 **CC BY 4.0** 授权发布（见 `LICENSE` 文件）：须署名，无附加限制。

---

## 10 Citing this archive / 如何引用

**EN** — The archive carries a DataCite DOI, which is the identifier to cite. A suggested citation:

> Zhang B. Data and code archive for "Autophagy-related prognostic signatures report gene expression, not autophagic flux: 169 coded reports from a census of 212" [Data set]. OSF; 26 October 2026. https://doi.org/10.17605/OSF.IO/9SRG3
> Live repository: https://github.com/lmxch00/Autophagy

**中文** — GitHub URL 稳定，但论文中以 DOI 为佳。本仓库当前状态的建议引用格式：

> Zhang B. Data and code archive for "Autophagy-related prognostic signatures report gene expression, not autophagic flux: 169 coded reports from a census of 212" [Data set]. OSF; 26 October 2026. https://doi.org/10.17605/OSF.IO/9SRG3
> Live repository: https://github.com/lmxch00/Autophagy

引文请用上行的 DOI（DataCite 签发，指向本归档的冻结快照）；第二行为可持续浏览的 GitHub 现行版。
