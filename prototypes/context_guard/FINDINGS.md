# Measured findings

Deterministic simulation; illustrative USD, no LLM/API results. The current saved benchmark contains 172 trajectory runs and 2,064 request records. These reuse four synthetic observation trajectories.

| Standard 1100-token policy | Correct | Simulated USD | Median local controller ms |
|---|---:|---:|---:|
| full | 3/12 | 0.002084 | 0.230 |
| recency | 11/12 | 0.020412 | 1.745 |
| relevance | 10/12 | 0.017504 | 1.922 |
| guard | 12/12 | 0.010037 | 1.200 |
| guard_no_gate | 12/12 | 0.011410 | 1.108 |
| guard_no_protection | 11/12 | 0.009929 | 1.174 |
| guard_no_dedup | 12/12 | 0.011857 | 1.173 |
| exact_local | 12/12 | 0.000000 | 0.000 |

Gate savings versus no gate: 12.0%, with 12/12 correctness in both. Full replay rejects nine requests at this capacity. With 8000 tokens, full replay is a feasible reference.

The rare fixture loses an unprotected identifier at 450 tokens. Removing deduplication yields a stale answer at 1100. At 8000, the one-request gate can cost more than proactive compaction over a trajectory. The exact-local reference answers all 48 observations with zero API cost; these structured fixtures need no LLM.

Current measured runner time: 3.336 seconds, excluding initialization and file writes. Tests: 17 pass. See [root experiment report](../../docs/09-experiments-and-results.md) and [stored results](results/results.json) for denominators, sweeps and limitations.
