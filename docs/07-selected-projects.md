# Selected projects

## Ledger Router

[Implementation and commands](../prototypes/ledger_router/README.md). Target users are API-gateway engineers evaluating model choice and finance owners reconciling bills. The prototype contributes an inspectable event ledger, conservative structured response identity, calibrated routing with separate rejection estimates, equal-cache baselines, drift/cold/attack fixtures, and billed failed attempts.

This combines lessons from [FrugalGPT](https://arxiv.org/abs/2305.05176), [AgServe](https://papers.neurips.cc/paper_files/paper/2025/hash/04132e28265a355456f86a1c3fec3bcd-Abstract-Conference.html), and [Cost-of-Pass](https://arxiv.org/abs/2504.13359). It does not claim a new routing algorithm or reproduction of their results.

The architecture is request identity → response cache → calibration and prefix-cost estimates → model → limited verifier → fallback → ledger. `shared/accounting.py` defines disjoint charge categories and fixture-based OpenAI/Anthropic/Gemini usage normalizers. These normalizers are not live integrations or invoice validation.

Release status: executable local research prototype. Default fixture savings trade some accuracy for price; stricter calibration and realistic holdouts are needed. A local deterministic solver beats all model policies on this structured toy problem, which is disclosed as an explicit baseline.

## Context Guard

[Implementation and commands](../prototypes/context_guard/README.md). Target users are agent-platform engineers managing repeated tool outputs and long histories. The prototype contributes online irreversible selection, protected facts, version-aware deduplication, budget rejection, and a prefix-cost gate. Selection never receives future questions or gold labels.

The architecture is new observation + retained memory → dedup/version check → protected record reservation → budgeted selection → current-cost compaction gate → actual serialized request → deterministic reader → ledger. The method is motivated by [ACON](https://arxiv.org/abs/2510.00615) and [Paritok](https://arxiv.org/abs/2608.24188), and adds a test fixture for their economic and correctness limitations rather than reproducing their learned compressors.

Release status: executable local research prototype. It preserves standard/protected fixture facts at adequate budgets, but loses unprotected rare facts and can make suboptimal horizon decisions. It assumes structured observations and trustworthy protection/version metadata. Production extraction, retrieval recovery and provider-specific cache behavior remain future work.

## Shared evaluation boundary

Both projects count the actual serialized fixture tokens using cl100k_base and report simulated prices separately from measured local runtime. Their cache configurations intentionally differ, so cross-project dollar totals should not be compared. Root [results](09-experiments-and-results.md) summarizes each against its own baselines. No paid model quality, GPU speedup, energy reduction or deployment savings is claimed.
