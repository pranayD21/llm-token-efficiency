# Experiments and results

**All model outcomes and dollar amounts below are deterministic simulations.** Token counts come from actual serialized fixture text; local CPU timings are observed. There were no paid API calls, GPU experiments or measured energy results. Python 3.14.7 and tiktoken 0.14.0 / cl100k_base were used. Simulation rate cards are dated 2026-09-06 and are distinct from the [current provider snapshot](../data/provider-pricing.json).

## Ledger Router

600 local calibration examples; seven scenarios with 240 requests each; twelve policies. The 20,160 policy-request records reuse 1,680 fixture requests, so they are correlated, not independent samples. `exact_local` is 100% correct at zero simulated API cost; these structured policy tasks do not need an LLM. The model experiment validates controller/accounting behavior only.

| Scenario | Policy | Correct | Total simulated USD | USD / successful request | Model attempts | Retries | Response hit rate |
|---|---|---:|---:|---:|---:|---:|---:|
| stationary | strong_a_cached | 240/240 | 0.071366 | 0.00029736 | 120 | 0 | 50.0% |
| stationary | full | 236/240 | 0.041441 | 0.00017560 | 120 | 0 | 50.0% |
| cold | strong_a_cached | 240/240 | 1.302720 | 0.00542800 | 240 | 0 | 0.0% |
| cold | full | 236/240 | 0.239841 | 0.00101627 | 240 | 0 | 0.0% |
| cache_affinity | strong_a_cached | 240/240 | 0.066964 | 0.00027902 | 121 | 0 | 50.0% |
| cache_affinity | full | 240/240 | 0.066964 | 0.00027902 | 121 | 0 | 50.0% |
| cache_affinity | cache_blind_routing | 240/240 | 0.234062 | 0.00097526 | 121 | 0 | 50.0% |
| wording_drift | strong_a_cached | 240/240 | 0.066601 | 0.00027750 | 120 | 0 | 50.0% |
| wording_drift | full | 238/240 | 0.134451 | 0.00056492 | 126 | 0 | 50.0% |
| wording_drift | no_verifier | 132/240 | 0.036950 | 0.00027992 | 120 | 0 | 50.0% |
| tenant_version_attack | strong_a_cached | 240/240 | 0.142733 | 0.00059472 | 240 | 0 | 0.0% |
| tenant_version_attack | full | 236/240 | 0.082882 | 0.00035120 | 240 | 0 | 0.0% |
| tenant_version_attack | unsafe_cache | 200/240 | 0.041441 | 0.00020721 | 120 | 0 | 50.0% |
| transient_failure | strong_a_cached | 240/240 | 0.076245 | 0.00031769 | 127 | 7 | 50.0% |
| transient_failure | full | 236/240 | 0.043981 | 0.00018636 | 127 | 7 | 50.0% |

On stationary fixtures, the full router reduces cost per successful request by **40.9%** against fixed strong A with equal cache access, but accuracy falls from 100% to 98.33%. This is a measured simulation tradeoff, **not quality-preserving savings**. It fails the proposed -1-percentage-point production noninferiority criterion.

The cache-affinity experiment charges one identical strong-A warm-up call to every non-local policy. Full routing matches the warmed fixed-A baseline; it does not beat it. Cache-blind selection instead chooses the cheaper cold strong B and incurs its worse cache-read rate. This demonstrates a mechanism under stipulated prices, not a universal provider advantage.

The wording-drift fixture separates changing model behavior from version invalidation. Verification/fallback maintains most correctness but costs more than fixed A. The verifier recognizes a stipulated shift, yet misses the amount-419 error even on normal requests. This makes its limitations visible. The unsafe amount-only cache serves cross-tenant mismatches. Fully cold traffic has zero prefix reads, verified by test and artifact reconciliation. Billed failed attempts and their retries are included in transient-failure totals.

### Token ledger example

| Stationary policy | Input | Output | Reasoning | Read-cache | Write-cache | Fallbacks | Verifications |
|---|---:|---:|---:|---:|---:|---:|---:|
| strong | 512640 | 2640 | 0 | 487424 | 25216 | 0 | 0 |
| strong_a_cached | 256320 | 1320 | 0 | 241664 | 14656 | 0 | 0 |
| full | 256320 | 1320 | 0 | 237568 | 18752 | 0 | 106 |
| no_response_cache | 512640 | 2640 | 0 | 483328 | 29312 | 0 | 212 |
| cheap | 512640 | 2640 | 0 | 487424 | 25216 | 0 | 0 |
| cascade | 572448 | 2948 | 0 | 540672 | 31776 | 28 | 240 |

`output_tokens` includes all generated outputs; reasoning is zero in these fixtures. Cache writes are a disjoint input category. Response hits make no model call and generate zero billed output. The fixed prompt deliberately has substantial repetition, so cache opportunity is unusually high. Full model calls, response misses, and verification CPU fees remain separate.

### Sensitivity and setup cost

- Target 0.95: observed fixture accuracy 98.33%, simulated cost $0.041441.
- Target 0.99: observed fixture accuracy 98.33%, simulated cost $0.041441.
- Target 0.999: observed fixture accuracy 100.00%, simulated cost $0.231091.

The separately computed counterfactual serving cost for 600 small-engine calibration responses is $0.043527. Actual calibration used local rules and paid $0. This counterfactual omits human/teacher label acquisition and is not silently added to the online-only totals. At production volume, amortize real setup and refresh costs.

[Complete router summaries](../prototypes/ledger_router/results/summary.json), [per-attempt ledgers](../prototypes/ledger_router/results/requests.jsonl), [workload](../prototypes/ledger_router/results/workload.jsonl), [sensitivity](../prototypes/ledger_router/results/sensitivity.json). Simulated model latency uses configured constants; local overhead fields measure only Python work and must not be presented as API latency.

## Context Guard

Four hand-authored observation trajectories of twelve turns each. The 172 trajectory runs and 2,064 request records include policy and budget sweeps, not independent samples. Full replay is the primary baseline; recency, relevance, and protection/dedup/gate ablations isolate mechanisms. Questions/gold are separate from controller input. The reader derives exact answers from the retained serialized facts.

At the standard default 1,100-token total budget:

| Policy | Correct | Rejections | Input | Cached | Output | Simulated USD | USD / correct request |
|---|---:|---:|---:|---:|---:|---:|---:|
| full | 3/12 | 9 | 1731 | 832 | 15 | 0.002084 | 0.00069480 |
| recency | 11/12 | 0 | 10675 | 832 | 70 | 0.020412 | 0.00185567 |
| relevance | 10/12 | 0 | 10611 | 2368 | 68 | 0.017504 | 0.00175036 |
| guard | 12/12 | 0 | 8192 | 3904 | 85 | 0.010037 | 0.00083640 |
| guard_no_gate | 12/12 | 0 | 7266 | 2112 | 85 | 0.011410 | 0.00095087 |
| guard_no_protection | 11/12 | 0 | 8198 | 3904 | 70 | 0.009929 | 0.00090262 |
| guard_no_dedup | 12/12 | 0 | 8411 | 3136 | 85 | 0.011857 | 0.00098810 |
| exact_local | 12/12 | 0 | 0 | 0 | 0 | 0.000000 | 0.00000000 |

The cache gate saves **12.0%** versus the otherwise identical guard without the gate, with 12/12 correct in both runs. It defers compaction 5 times. Full replay rejects nine requests at this capacity; its smaller bill does not indicate a successful trajectory.

At 8,000 tokens, full replay provides a feasible matched-quality reference:

| Scenario | Policy | Correct | Simulated USD | Peak serialized input |
|---|---|---|---:|---:|
| standard | full | 12/12 | 0.014838 | 2979 |
| standard | guard | 12/12 | 0.011898 | 2106 |
| standard | guard_no_gate | 12/12 | 0.012282 | 2106 |
| rare | full | 12/12 | 0.014908 | 2982 |
| rare | guard | 12/12 | 0.011968 | 2109 |
| rare | guard_no_gate | 12/12 | 0.012352 | 2109 |
| stale | full | 12/12 | 0.016275 | 3449 |
| stale | guard | 12/12 | 0.012346 | 2201 |
| stale | guard_no_gate | 12/12 | 0.012282 | 2106 |

At the feasible 8,000-token budget, cumulative input compression (full replay divided by guard) is standard: 1.26x; rare: 1.26x; stale: 1.32x. These are within-fixture matched-quality comparisons, not model quality experiments. At the 1,100-token budget, the cache gate actually retains more cumulative input than the no-gate ablation while costing less, illustrating why raw token minimization is the wrong economic objective.

Failure cases: the guard loses an unprotected rare identifier at a 450-token budget (11/12 correct). Disabling version deduplication produces a stale answer at 1,100 tokens (11/12). Every context policy rejects all default 100-token requests, yielding null cost per success. The current-request gate can lose against proactive compaction over a whole trajectory; the stale 8,000-token comparison demonstrates this. Protected records come from annotations, not an automatic safety guarantee.

[Full context results](../prototypes/context_guard/results/results.json), [serialized request ledgers](../prototypes/context_guard/results/requests.jsonl), and [fixture design](../prototypes/context_guard/README.md). Compression ratios can be computed against full replay at equal budget; peak and cumulative input are both present, and must not be interchanged. The exact-local reference answers all 48 observations correctly at zero simulated API cost.

The final context benchmark measured 3.336 seconds of local runner time, excluding initialization and result writes. Local timings vary across runs. There are no confidence intervals for production savings: the fixtures are too small and constructed for failure testing.

## Tokenization experiment

The same Hindi string used 31 cl100k_base tokens and 11 o200k_base tokens; the Chinese sample used 8 and 7; the English and JSON samples tied. These are observed encodings of four strings, not evidence that changing a provider/model preserves task quality. [Exact strings and counts](../results/tokenizer-comparison.json).

## Verification and interpretation

Fourteen router/accounting tests and seventeen context tests pass. The independent root verifier re-tokenizes stored requests/outputs, reconciles each charge and summary, checks hard budgets and prefix state, and verifies nonempty deliverables and citation identity. See [verification.json](../results/verification.json) and the [work log](11-work-log.md). External source access exceptions are separately recorded in [link checks](../results/link-checks.json).

These runs validate working local systems and disprove several overbroad savings claims. They do not establish the selected projects as production improvements. Next, replace mock behavior with pinned model observations, objective labels and chronological session traces, keeping the same accounting contract and equal-cache baselines.
