# Search protocol

Search date and cutoff are **2026-09-06 PDT**. This is a purposive, reproducible mapping review, not an exhaustive systematic review or meta-analysis. It includes 39 primary research works, plus official product documentation and tooling sources. We did not preserve a complete universe of search-engine hits; therefore no PRISMA-style screened/rejected population count is claimed.

## Sources and procedure

Discovery used the built-in web index with domain-focused searches of arXiv, ACL Anthology, OpenReview, PMLR/ICML, NeurIPS, ICLR, author repositories, and official provider documentation. OpenAlex's public works endpoint found LLMLingua and LLMLingua-2. Crossref title search returned unrelated articles; an exact DOI request verified LLMLingua-2 instead. Raw responses are under [`data/raw`](../data/raw/). These are distinct metadata checks, not two independent experiments supporting a paper's conclusions.

Two research agents covered routing and inference/reasoning. The coordinator covered caching, context management, tools, pricing, reconciliation, and key-claim checks. Agent reports were discovery inputs. Canonical paper records were fetched separately; high-impact numerical and gap claims were checked in full text or extracted PDF tables. `update_plan` was not exposed in this session; the work log records the plan and phase transitions instead.

## Executed query families

The complete compact query ledger is [`search-queries.json`](../data/search-queries.json). Representative exact searches:

```
FrugalGPT RouteLLM RouterBench arxiv
LLM routing cache aware routing cascade cost successful task 2025 2026
LLM routing workload distribution drift caching fallback cost cascade
site.arxiv.org "routing" "non-stationary"
LLM joint model routing semantic caching fallback optimization paper arxiv
site.arxiv.org semantic caching LLM correctness privacy 2025 2026
site.arxiv.org agent context memory compression 2026 2025
site.aclanthology.org LLMLingua-2 prompt compression data distillation
site.arxiv.org RECOMP retrieval compression
site.arxiv.org SGLang RadixAttention CacheBlend LMCache
site.arxiv.org 2026 efficient reasoning early stopping uncertainty token budget
site.arxiv.org 2025 token budget forcing thinking optimal length reasoning
site.arxiv.org 2026 multi agent token efficiency overhead
site.arxiv.org tokenization efficiency language models tokens vocabulary inference
site.developers.openai.com API pricing cached tokens batch processing
site.platform.claude.com docs pricing prompt cache 5 minute 1 hour
site.ai.google.dev gemini-api docs pricing context caching storage
```

Follow-up searches used exact titles and identifiers for each included paper. Searches for vCache found an ICLR 2026 record, but the canonical page returned a browser challenge. It remains a discovery-only related-work candidate, excluded from numerical synthesis. An informal ACON reference incorrectly linked arXiv:2507.00379, which is a vector-database paper. The verified ACON identifier is 2510.00615. That error is recorded rather than propagated.

## Eligibility and version handling

Include primary studies with a clear efficiency mechanism or relevant diagnostic/economic evaluation, and dated official product rules that affect deployment accounting. Include preprints, but label them separately from peer-reviewed publications. Exclude unsupported marketing savings, speculative token prices, cryptocurrency token economics, papers after the cutoff, and unrelated model-compression work with no relevant inference connection. Informal sources can supply leads, never quantitative evidence.

Deduplicate by arXiv base identifier or DOI plus normalized title. A preprint and accepted version are one work. The CSV distinguishes first-publication metadata from notes on the version used for numerical claims. Where a venue was not independently established, retain `preprint; later venue not verified`. Sources with missing metrics carry `not reported`; in this repository that means not established in the inspected evidence, not proof the entire paper omits it. Do not average incomparable benchmark quality measures or multiply headline savings across methods.

## Citation tracing

| Earlier work | Forward discovery / citing work | Verification |
|---|---|---|
| FrugalGPT | [RouterBench §2 and references](https://arxiv.org/html/2403.12031v2) | Sequential generation/judging and exact earlier identifier |
| RouteLLM | [AgServe §7.2 and reference 37](https://papers.nips.cc/paper_files/paper/2025/file/04132e28265a355456f86a1c3fec3bcd-Paper-Conference.pdf) | Coordinator extracted PDF; RouteLLM used as baseline |
| Speculative decoding | [EAGLE-3 §2.1](https://arxiv.org/html/2503.01840v1) | Target-distribution preservation and earlier ICML citation |
| PagedAttention | [Sarathi-Serve reference 50](https://arxiv.org/html/2403.02310v1) | Earlier KV-memory method identified |
| LLMLingua / earlier context methods | [ACON related work](https://arxiv.org/html/2510.00615v1) | Backward tracing to document-oriented compression |

This is bounded forward/backward tracing through citing papers, not a complete citation-index traversal.

## Coverage and stopping rule

Coverage spans routing, six caching levels, context/retrieval/memory, adaptive reasoning/output, tokenization, specialization, speculative inference, scheduling, and agent communication. English-language indexed sources dominate. Paywalled full texts, vendor-internal routing, energy measurements, multilingual quality, and negative unpublished results remain weakly covered. Late-2026 preprints receive lower confidence than replicated work. Stop discovery once every required category has primary support, key counterexamples have been checked, and remaining uncertainty is explicit. Further research should target trace availability and comparable success labels rather than accumulate more headline compression ratios.
