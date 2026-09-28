# Project portfolio

Scores are reviewer judgments on a 1–5 scale, with 5 favorable. They are not empirical measurements. Savings and quality each weigh 20%; novelty 10%; feasibility 10%; time-to-prototype 10%; evaluation 10%; reproducibility 10%; deployment usefulness 5%; low risk 5%. Novelty means a useful contribution relative to the named prior art, not priority established by this review.

| Project / gaps | Savings | Quality | Novelty | Feasible | Fast | Evaluate | Reproduce | Useful | Low risk | Weighted |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Ledger Router + full-event benchmark / G1,G6 | 4 | 4 | 3 | 4 | 4 | 5 | 5 | 5 | 3 | 4.10 |
| Context Guard + cache-break-even tests / G2,G3 | 4 | 4 | 3 | 5 | 4 | 5 | 5 | 4 | 3 | 4.15 |
| Semantic cache risk service / G4 | 4 | 3 | 2 | 4 | 4 | 3 | 4 | 5 | 2 | 3.45 |
| Mixed-domain reasoning budget learner / G5 | 5 | 3 | 4 | 2 | 2 | 3 | 2 | 5 | 2 | 3.25 |
| Learned horizon-aware joint controller / G1,G2,G5 | 5 | 3 | 4 | 2 | 1 | 2 | 2 | 5 | 1 | 3.00 |
| GPU draft/batch optimizer / inference | 2 | 5 | 2 | 2 | 1 | 3 | 2 | 4 | 2 | 2.70 |

The weights and calculated scores are also in [`portfolio.json`](../data/portfolio.json). Choose the first two because they test the strongest economic and correctness interactions with observable failure cases, reusable ledgers, and local reproducibility. Their mechanistic novelty is modest. Their immediate value is exposing when a seemingly cheaper policy fails.

The semantic-cache service faces direct prior art in [LaCache](https://arxiv.org/abs/2608.01718), [FreshCache](https://arxiv.org/abs/2607.04281) and [Grounded Cache Routing](https://arxiv.org/abs/2605.27494). A lexical cache toy alone would be too weak a novelty claim; the router includes only a deliberately unsafe reuse ablation and a conservative structured identity cache. A real learned semantic-cache service remains a separate project.

The reasoning learner has high possible value, but [SelfBudgeter](https://arxiv.org/abs/2505.11274) and [ESTAR](https://arxiv.org/abs/2602.10004) set a much stronger experimental bar than local scaffolding. The GPU project primarily improves execution, and needs measured accelerator tests. These are deferred for evidence and infrastructure reasons, not because token accounting makes them unimportant.
