# Literature gaps

These gaps are bounded findings from the included evidence, not claims that no paper anywhere addresses them. “Evidence-backed gap” means a concrete limitation is visible in the selected papers. “Hypothesis” means the proposed combination still needs disconfirmation and experiments.

## G1: Audit complete costs under heterogeneous model and cache switching

**Classification:** evidence-backed benchmarking/engineering gap in the selected comparison set; the benefit of a new controller is a hypothesis.

[FrugalGPT](https://arxiv.org/abs/2305.05176) already counts cascade calls. [AgServe](https://papers.neurips.cc/paper_files/paper/2025/hash/04132e28265a355456f86a1c3fec3bcd-Abstract-Conference.html) already combines cache management, upgrades, retries, and resources. [Cost-of-Pass](https://arxiv.org/abs/2504.13359) already connects cost and success. What remains weakly supported here is one reproducible comparison joining provider-specific read/write/retention rules, heterogeneous-model switch costs, verification and all failed attempts, objective completed tasks, and chronological drift.

API-gateway and agent-platform engineers would benefit because a cheap first call can raise the final bill. Existing component benchmarks or static response tables do not establish the economics of a stateful deployment.

**Falsifiable question:** Against fixed-model-with-cache, ordinary cascade, session-sticky, and cache-blind routing, can an all-in cost policy reduce cost per successful task by at least 15%, while its paired success-rate difference has a 95% lower bound above -1 percentage point on a chronological holdout?

**Risks:** Weak calibration, expensive verification, cache churn, inaccurate price normalization, and a stronger fixed baseline may eliminate savings. The local Ledger Router already contains drift cases that cost more. The 15% threshold is a proposed release criterion, not a measured literature result.

## G2: Decide when compression is worth destroying a cached prefix

**Classification:** evidence-backed economic/engineering limitation; proposed policy improvement is a hypothesis.

[ACON's cost analysis](https://arxiv.org/html/2510.00615v1) explicitly identifies the problem. [Paritok](https://arxiv.org/abs/2608.24188) also makes compressor cost part of the economics. Thus “compression has overhead” is established; a useful contribution would be a provider-neutral, horizon-sensitive policy with auditable break-even decisions.

Long-running agents benefit when they can preserve cheap reusable history until compaction is necessary. A current-request gate cannot predict every future request, so it is an intentionally limited baseline for horizon-aware decisions.

**Question:** Can a controller reduce cumulative deployment cost by 10% against periodic compaction and full replay at matched feasible quality and context capacity, counting cache rewrites and compressor calls?

**Success criterion:** All protected invariants retained, no increase in severe failures, positive cost savings on at least two real trace families and no more than 5% cost regression on a predefined cold-cache subset. **Risks:** Future access patterns are unknown; a short-sighted gate can delay useful compaction; small contexts may force information loss regardless of policy.

## G3: Rare facts and freshness under repeated, irreversible memory updates

**Classification:** evidence-backed evaluation weakness, not absence of memory-control research.

[LLMLingua-2](https://aclanthology.org/2024.findings-acl.57/) evaluates broad tasks, while [ACON](https://arxiv.org/abs/2510.00615) addresses long trajectories and [Paritok](https://arxiv.org/abs/2608.24188) exact spans. Average scores do not certify rare constraints after many updates. Tool facts can arrive late, conflict at the same version, or be irreversibly evicted.

The beneficiaries are coding and operational agents that must preserve identifiers, permissions, negation, and current state. Existing results do not supply a general guarantee for arbitrary rare downstream queries.

**Question:** Does provenance-aware deduplication with explicit protection reduce rare-fact failures relative to recency/relevance truncation at the same budget? **Criterion:** Zero protected-fact loss or explicit abstention; report unprotected rare-fact recall and severe failures separately, with at least 1000 independent rare cases before claiming a <1% rate. **Risks:** Protection labels are incomplete; overprotection exhausts capacity; missing version tombstones permit stale resurrection. Context Guard tests these failures rather than hiding them.

## G4: Semantic reuse that is both safe and useful under drift

**Classification:** engineering hypothesis with strong prior art.

[MeanCache](https://arxiv.org/abs/2403.02694), [LaCache](https://arxiv.org/abs/2608.01718), [FreshCache](https://arxiv.org/abs/2607.04281), and [Grounded Cache Routing](https://arxiv.org/abs/2605.27494) already address context, attacks, freshness or evidence. The remaining target is cross-tenant authorization, temporal correctness and useful hit rates with verification overhead in the same bill.

**Question:** On a held-out stream with changed documents and near-duplicate negations, can reuse save 20% of task cost at <0.5% false accepted hits and no tenant leakage? **Beneficiaries:** support/RAG applications. **Why previous work is insufficient for this claim:** single-family tests, synthetic drift or different error denominators cannot establish it for a new deployment. **Risks:** Rejecting almost every hit looks safe but saves nothing; embeddings retain sensitive information; evaluator errors can conceal wrong reuse.

## G5: Quality-calibrated reasoning budgets across domains

**Classification:** scientific/benchmarking hypothesis.

[SelfBudgeter](https://arxiv.org/abs/2505.11274) and [ESTAR](https://arxiv.org/abs/2602.10004) demonstrate useful budget control and also measurable tradeoffs. [Compute-optimal allocation](https://arxiv.org/abs/2408.03314) depends on difficulty estimation. Evidence remains weaker for mixed-domain requests, changing models and budgets that include the estimator's own cost.

**Question:** Can a calibrated stop/router policy preserve a -1-point noninferiority margin across math, code and document tasks while reducing all generated tokens 25%? **Beneficiaries:** reasoning API operators. **Risks:** verbal confidence and answer stability can remain high on wrong answers; APIs may not expose probabilities; training and domain adaptation are expensive. Not selected for immediate implementation because meaningful validation needs real models and multiple datasets.

## G6: Portable accounting and economically meaningful benchmarks

**Classification:** evidence-backed engineering gap; standardization opportunity is speculative.

[Provider rules](03-literature-review.md#joint-systems-and-deployment-economics) differ in token categories, cache writes/storage, service tiers and context thresholds. Static router results and token-only comparisons obscure those differences. A neutral event schema should retain provider raw usage, schema version, tokenizer, rates, and charge attribution.

**Question:** Can a normalizer reproduce provider invoices within 1% across three providers and identify all intentionally injected duplicate/omitted charges? **Users:** platform cost owners and benchmark authors. **Risks:** invoices aggregate or lag; providers change schemas; unavailable hidden tokens prevent exact reconstruction. The local accounting module tests category boundaries, but invoice reconciliation remains untested.
