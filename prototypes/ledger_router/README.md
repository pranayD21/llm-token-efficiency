# Ledger Router

A runnable, deterministic experiment for model routing with explicit cost ledgers. It tests calibration, response reuse, provider-like prefix charges, verification, retries, and cache-sensitive model choice. It is not a deployed LLM gateway, a trained natural-language router, or a reproduction of a paper's performance.

Run from the repository root:

```sh
.venv/bin/python prototypes/ledger_router/benchmark.py
.venv/bin/python prototypes/ledger_router/sensitivity.py
.venv/bin/python -m unittest discover -s prototypes/ledger_router -p 'test_*.py'
```

Install the root pinned requirements first if needed. `config.json` controls the seed, target, cache lifetimes/block size, model rate cards and verifier cost. `sample.jsonl` is a small generated workload. `results/workload.jsonl` is the complete evaluation set. The benchmark uses 600 separate calibration examples and 240 requests in each of seven scenarios, evaluated under twelve policies. No test labels enter the decision rule.

## Architecture and data flow

```
request + tenant/version -> scoped response lookup
  -> calibrated bucket + actual prefix state -> estimated all-in model cost
  -> small or strong deterministic engine -> limited local verifier
  -> fallback if rejected -> response cache -> per-attempt ledger
```

`core.py` contains routing and the mock engine seam. The engine models a small policy checker and two strong checkers over explicit structured fields. The small engine ignores blocked exceptions, mishandles a changed wording class, and has an undetected error at amount 419. Strong engines implement the same correct task logic independently of the evaluator. The verifier validates schema/version and rejects known exceptional wording or blocked cases; it does not verify approval correctness. `gold()` is used only for offline calibration/evaluation, never to accept a live response. A real backend must replace the mock engine and return provider-observed usage; no API adapter or credentials are configured.

Calibration uses a Wilson lower confidence bound on small-engine accuracy in an observable request bucket. Verifier rejection frequency is calibrated separately for expected fallback cost. This is a fixed hand-chosen partition, with IID assumptions that fail under drift. The cumulative rejection guard disables small-model use after at least ten verified calls when rejection exceeds 10%; it is a heuristic, not a learned drift detector or calibrated guarantee. Silent wrong answers pass it.

Response identity includes tenant, policy version, amount, limit, blocked state and wording. It represents structured equivalence, not an embedding-based semantic cache. Production identity must also include all relevant authorization, source state, system prompt and output-schema versions. Response TTL is measured from creation. Prefix state is scoped to tenant, version and model, stores the last prompt only, and refreshes on a model attempt. Logical prefix matching is not portable KV transfer between models.

## Baselines and interventions

| Policy | Configuration |
|---|---|
| `strong` | Always strong A; prefix cache; no response reuse. Naive primary baseline. |
| `strong_a_cached`, `strong_b_cached` | Fixed model with the same response cache as the router. Fairer attribution baselines. |
| `cheap` | Always small, no verification/response reuse. |
| `cascade` | Small followed by verification and possible strong fallback. |
| `full` | Calibrated all-in routing, response cache, prefix-aware selection and rejection guard. |
| `no_response_cache` | Full routing with response reuse disabled; prefix caching retained. |
| `cache_blind_routing` | Prefix state ignored in every cost estimate, but actual cache reads remain billed normally. |
| `no_verifier` | No verification or rejection-driven fallback; demonstrates accepted errors. |
| `no_drift_guard` | Verification/fallback retained; cumulative rejection guard disabled. |
| `unsafe_cache` | Intentionally keys response reuse by amount only, omitting authorization and policy context. |
| `exact_local` | Direct deterministic policy code, no model calls or token bill. This is the appropriate solution for these structured tasks outside a router experiment. |

The full router minimizes immediate estimated cost, not total future workload cost. A cheaper cold strong model can lock the policy into a worse cache rate; the results expose this limitation.

## Workloads and cost contract

`stationary` changes the policy version halfway through. `wording_drift` changes wording without changing version; `drift` changes both. `tenant_version_attack` reuses amounts across tenants with different limits. `cold` spaces requests 301 time units apart, exceeding both TTLs. `cache_affinity` initializes the same strong-A prefix state for every non-local policy using one explicit warm-up call, whose full cost and tokens enter the first request ledger. No scenario label changes routing behavior. `transient_failure` injects an initially failed model attempt every seventeenth eligible request; response hits bypass the attempt entirely.

Failed attempts in this simulation are fully input-billed with zero output and populate prefix state; the retry can read that state. This is a stated fixture assumption, not a provider error-billing rule. Each retry and fallback is counted, and failed-attempt cost enters cost per success. There is at most one injected transient failure per model invocation. No real network calls occur.

`shared/accounting.py` partitions input into uncached/read/write tokens and makes reasoning a subset of output. Here all non-read input receives the illustrative total write rate. Configured models are fictional; the separately documented current provider rates are not substituted. The fixed prompt is deliberately long and highly reusable, which favors caching. Tokenization uses tiktoken 0.14.0 / cl100k_base on exact serialized fixture text, without vendor chat framing. Outputs have no reasoning tokens. Model latency is stipulated at 35/250 ms; local controller runtime is measured separately and should not be confused with inference latency.

`summary.json` reports accuracy, actual tokenized fixture counts, simulated cost per request/success, calls, fallback/retry counts, cache hits and local overhead. `requests.jsonl` contains every attempt ledger and answer. `sensitivity.json` varies the target and verifier fee. `calibration-cost.json` separately prices a counterfactual deployment of the small-model calibration responses; actual paid spend is zero. The calibration labels come from local rules, not a billed teacher. Production label acquisition and refresh would add cost.

## Findings and limits

See the repository [experiment report](../../docs/09-experiments-and-results.md). The default target allows some quality loss. Savings at 98.33% accuracy cannot be presented as equal-quality savings against 100% fixed engines. A stricter target can recover fixture accuracy while losing the economic advantage. The exact-local baseline establishes that an LLM is unnecessary for this synthetic task itself; the prototype is for accounting/controller validation.

There are no embeddings, natural-language extraction, genuine model uncertainty, live provider calls, distributed cache, invoice reconciliation, encryption, concurrent writes or online retraining. Repeated templates are correlated; request counts do not establish statistical confidence on production traffic. Tests cover partition validation, nonfinite prices, calibration, retry/fallback charges, cache identity, fully cold behavior, scenario-label independence, and known verifier failures. Novelty is deliberately bounded by [FrugalGPT](https://arxiv.org/abs/2305.05176), [AgServe](https://papers.neurips.cc/paper_files/paper/2025/hash/04132e28265a355456f86a1c3fec3bcd-Abstract-Conference.html), and [Cost-of-Pass](https://arxiv.org/abs/2504.13359).
