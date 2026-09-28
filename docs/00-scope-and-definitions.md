# Scope and definitions

The target is minimum total deployment cost at a defined task-success level. The audience is engineers evaluating API gateways, retrieval systems, and long-running agents. This repository is a bounded evidence review and two executable local experiments, not a claim of production savings.

Search and literature cutoff: **2026-09-06, America/Los_Angeles**, verified with the environment clock. The corresponding UTC date during work is September 7. Foundational work begins in 2022; 2025–2026 work is treated as current. No private project sources were available; `sources/` was empty and remains untouched.

## Accounting contract

For a workload of submitted tasks, report `sum(all attributable deployment expenses) / count(successful tasks)`, alongside success rate and latency constraints. A zero-success denominator is undefined, represented as JSON null. Do not exclude failed requests from the numerator. This is a realized workload ratio; it is not automatically the expected number of independent retries needed for one successful answer. [Cost-of-Pass](https://arxiv.org/abs/2504.13359) supplies the economic motivation and also demonstrates that cheap guessing can game a ratio without a quality constraint.

Partition input tokens into uncached, cache-read, and cache-write categories. Output totals include reasoning where the provider bills it as output; the reasoning field is a subset, not an extra charge. Add tool charges, cache storage, verifier/model calls, retrieval, retries, and amortized training separately. A cache-write multiplier is the total rate for that category, not an extra charge unless the provider explicitly defines it that way.

`C = (U*p_input + R*p_read + W*p_write + O*p_output)/1e6 + storage + tools + verification + amortized_setup`.

A complete service objective also constrains success rate, tail latency, privacy, and severe-error frequency. The local router uses a 0.95 calibration target; that is an engineering setting, not a formal deployment guarantee. Context tests use exact answer matching and report rare-case failures separately.

## Four different mechanisms

| Class | Examples | What can fall | What must be counted elsewhere |
|---|---|---|---|
| Reduce content | Pruning, retrieval selection, terse answers, early stopping | Input or generated output | Compression, retrieval, budget-estimation calls; quality loss |
| Reduce billing | Cheaper-model routing; discounted cache reads; batch API | Dollar cost with unchanged logical tokens | Failed cheap attempts, write fees, storage, delayed completion |
| Improve execution | Speculative decoding; paged attention; quantization; scheduling | Serial latency, memory, accelerator work | Drafts, rejection, hardware utilization; token count can remain unchanged |
| Shift work | Distillation, offline summaries, cached embeddings | Online expense | Teacher calls, training, indexing, storage, refresh and amortization |

Prompt/prefix caching reuses model computation. Exact response caching bypasses generation for the same authorized request. Semantic caching reuses a response for a different request based on an equivalence hypothesis. KV caches contain model- and position-dependent state; they are not portable between arbitrary model families. [CacheBlend](https://arxiv.org/abs/2405.16444) studies partial recomputation for non-prefix reuse; [speculative decoding](https://proceedings.mlr.press/v202/leviathan23a.html) preserves the target distribution while changing execution.

## Assumptions

Initial prototypes use synthetic, public-shaped data and deterministic engines. No paid model, GPU rental, account change, or external publication is required. The installed tokenizer counts actual serialized fixture text; model behavior, prices, network latency, and provider cache residency are simulated. Development-time assistant usage and research calls are outside prototype deployment costs and were not metered. Labeled calibration work is reported separately rather than silently treated as free production work.
