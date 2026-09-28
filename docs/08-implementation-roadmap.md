# Implementation roadmap

The delivered milestone is a runnable research repository. Production release remains gated on real-model quality, invoice reconciliation, and realistic traces.

## Product and users

Build an evaluation library first, then an optional service wrapper. Platform engineers submit request/attempt traces and get quality-constrained cost comparisons. Agent builders submit versioned observation histories and get retention, cache-invalidation and rare-failure diagnostics. Finance owners need charge provenance rather than a single “tokens saved” counter.

## Target architecture

```
workload + gold registry -> replay/evaluation runner
provider adapters -> immutable usage events -> normalized charge ledger
request/session state -> cache registry + calibration -> action policy
observations -> versioned memory + protected facts -> context policy
all outputs -> task scorer -> quality/cost/latency reports -> release gate
```

Preserve provider raw usage alongside normalized events. Separate response, prefix, retrieval and tool caches. Include request, attempt, session, tenant, model, prompt version, tokenizer, price version, timing, failure class and billed category. A durable event store supports retries without duplicate charges. Store raw content only when required and authorized; default reports should use hashes and aggregate labels.

## Milestones and dependencies

| Milestone | Work and output | Dependency | Exit criterion | Effort estimate |
|---|---|---|---|---|
| M0 delivered | Literature dataset, local controllers, tests, ablations, reproducible results | Python and pinned tokenizer/parser | Artifact and ledger checks pass | Completed in this session |
| M1 trace contract | Provider raw-usage fixtures, schema versions, idempotent event IDs, offline replayer | Public schemas; sanitized traces | All charges reconciled; zero duplicate retries in injected-error tests | 3–5 engineering days |
| M2 real-model pilot | Pin two model families; measured usage, objective labels, fixed-cache baselines | Authorized API budget or local models | ≥1000 unique tasks; chronological split; independent judge calibration | 1–2 weeks plus label work |
| M3 joint evaluation | Compare fixed cached model, ordinary cascade, session-sticky, cache-blind, full policy; context gate ablations | M2, realistic timestamps and cache states | Quality noninferiority and positive success-normalized savings | 1–2 weeks |
| M4 hardening | Tenant isolation, encryption, retention/deletion, concurrency, bounded retries, price refresh | Security review and service requirements | No cross-tenant reuse; outage and budget tests pass | 1–2 weeks |
| M5 shadow then canary | Decision-only replay; low-volume deployment; rollback controls | M3/M4 gates | Stable per-stratum success and bill reconciliation | 1–2 weeks monitoring |

Effort estimates are planning assumptions, not commitments or measured development hours.

## Datasets and experimental plan

Use [RouterBench](https://arxiv.org/abs/2403.12031) for an inexpensive static routing baseline, with dataset license and split checks before download. It cannot replace live cache evaluation. Add public tasks with objective answers or tests: arithmetic, code execution, structured document extraction, and multi-step agent environments such as those evaluated by [ACON](https://arxiv.org/abs/2510.00615). Obtain authorized, deidentified session traces for repetition, timestamps, failure and source-update distributions. Do not substitute paraphrase counts for independent task count.

Separate calibration, policy selection and final chronological test sets. Group by original task/document/session to prevent duplicate leakage. Run matched-policy evaluations with identical model versions, cache budgets and starting states. Measure all attempts, verifier/embedding/compressor overhead, setup cost, cache storage and tool fees. Report per-stratum accuracy, rare failures, p50/p95/p99 task latency, cumulative input/output/reasoning/cache tokens, dollar cost and cost per successful whole task.

Vary repetition, arrivals, TTL, output length, verifier error/cost, model-price ratios, context capacity, policy updates and model outages. Ablate one component at a time, then test interactions. Bootstrap independent task/session groups for paired confidence intervals; use a preregistered noninferiority margin. Retry success assumptions must account for correlated failures. Use human-reviewed severe-error labels where exact scoring is insufficient.

## Infrastructure and operating-cost assumptions

M0 needs one CPU process and local disk; actual paid API spend is $0. Disk/runtime measurements are in the environment/results artifacts. The virtual environment is separate from read-only synced project sources.

For an illustrative pilot of 1000 tasks with 2000 input and 300 output tokens each, at assumed rates $2/$8 per million and no caching, one model pass costs `(2,000,000*2 + 300,000*8)/1e6 = $6.40`. Ten configurations cost $64 before verification, retries, labels, embeddings or storage. Doubling for those factors yields a provisional $128 budget, not a provider quotation. Use [dated current rate cards](../data/provider-pricing.json) to replace assumptions before running. Set hard spend ceilings and stop conditions. No such paid run has been initiated.

Self-hosted evaluation adds GPU rent and idle time. Do not use speculative-decoding speedups as a direct rent reduction without matching quality, utilization and throughput. Training/distillation should pass `setup_cost / positive_per_task_saving` break-even volume, with recurrent refresh cost included.

## Release and monitoring

A production candidate must pass the G1 -1-point quality noninferiority margin and ≥15% cost-per-success improvement on a locked realistic holdout, with no severe-error regression. The default local router does not meet that quality margin against the perfect fixture baseline. Memory release requires exact protected-fact retention or explicit rejection, version-conflict abstention, and a recovery path for unprotected evidence.

Begin in shadow mode, then canary only after authorization and passed gates. Monitor success by task/domain/language, verifier false accept/reject rates, cache age and useful-hit rate, failed-attempt charges, bill/ledger differences, budget rejection, missing critical facts, queueing and tail latency. Roll back when the quality margin, privacy boundary or spend ceiling fails. Snapshot prices and model versions; alert on missing usage fields rather than silently imputing zero.

## Security, privacy and open decisions

Authorize cache access before lookup; separate tenants and policy/source versions. Enforce retention/deletion on answers, embeddings, logs and KV/application state. Do not cache secrets or tool outputs merely because they repeat. Treat retrieved text as untrusted data, not controller instructions. Validate schemas, finite costs, versions and idempotency keys. A semantic cache needs attack and stale-content tests, including negative queries and permissions changes.

Open decisions: target production workload; success rubric and severe-error tolerance; provider access and model versions; paid budget; source/trace licenses; retention region; whether a deterministic solver can eliminate the model; and whether a horizon-aware policy can beat the simpler fixed cached baseline. These decisions do not prevent running the delivered local prototypes.
