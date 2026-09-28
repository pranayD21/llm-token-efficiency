# LLM token efficiency: evidence and runnable experiments

Reduce the cost of completing a task at a defined quality level. This repository contains a **39-work primary-source review**, a dated provider-pricing snapshot, two runnable local prototypes, and reconciled benchmark artifacts. Literature cutoff: **September 6, 2026 (PDT)**.

The strongest opportunity is auditable evaluation across model choice, cache state, failed attempts, context loss and workload drift. Joint routing/caching already exists; the review explicitly accounts for AgServe, LLMBridge and other counterexamples.

**Results are local simulations, not measured LLM/API savings.** Context Guard saved 12.0% against its no-gate ablation at equal 12/12 standard-fixture correctness. Ledger Router's default stationary savings came with accuracy loss, and it regressed economically under drift. The [experiment report](docs/09-experiments-and-results.md) gives exact denominators, fairer cached baselines and failure cases. Both projects include a deterministic local reference showing that their structured fixtures can be solved without an LLM.

## Run

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --only-binary=:all: -r requirements.lock
.venv/bin/python prototypes/ledger_router/benchmark.py
.venv/bin/python prototypes/ledger_router/sensitivity.py
.venv/bin/python prototypes/context_guard/benchmark.py
.venv/bin/python -m unittest discover -s prototypes/ledger_router -p 'test_*.py'
.venv/bin/python -m unittest discover -s prototypes/context_guard
.venv/bin/python scripts/build_results_report.py
.venv/bin/python scripts/verify_repository.py
```

The environment and vocabulary caches were installed and used during this project. Benchmarks run offline with those caches. See [setup and tool provenance](docs/01-tooling-audit-and-use-ledger.md) for hashes, permissions, failures and limitations.

## Documentation

| File | Contents |
|---|---|
| [00 Scope and definitions](docs/00-scope-and-definitions.md) | Cost-per-success contract; token/billing/compute distinctions |
| [01 Tool audit and use ledger](docs/01-tooling-audit-and-use-ledger.md) | Installed versions, actual use, rejected candidates, security limits |
| [02 Search protocol](docs/02-search-protocol.md) | Sources, exact searches, eligibility, tracing and coverage limits |
| [03 Literature review](docs/03-literature-review.md) | Evidence synthesis across every required topic |
| [04 Evidence matrix](docs/04-evidence-matrix.md) | Quality, token, price, latency, compute and reproducibility comparisons |
| [05 Literature gaps](docs/05-literature-gaps.md) | Prior art, falsifiable questions, success criteria and failure risks |
| [06 Project portfolio](docs/06-project-portfolio.md) | Weighted scores and selection rationales |
| [07 Selected projects](docs/07-selected-projects.md) | Product definitions, architecture and delivered scope |
| [08 Implementation roadmap](docs/08-implementation-roadmap.md) | Real-model evaluation, costs, release gates and deployment plan |
| [09 Experiments and results](docs/09-experiments-and-results.md) | Executed benchmarks, ablations, measured counts and limitations |
| [10 Risks and open questions](docs/10-risks-limitations-and-open-questions.md) | Coverage, simulation and deployment limits |
| [11 Work log](docs/11-work-log.md) | Commands, corrections, versions and verification |

## Projects and evidence

- [Ledger Router](prototypes/ledger_router/README.md): scoped response reuse, calibration, cache-aware immediate cost, verifier/fallback/retry accounting. [Summary](prototypes/ledger_router/results/summary.json).
- [Context Guard](prototypes/context_guard/README.md): irreversible memory selection, protected facts, versioned tool reuse and compaction economics. [Summary](prototypes/context_guard/results/results.json).
- [Literature CSV](data/literature.csv), [JSON](data/literature.json), [BibTeX](references.bib), [search ledger](data/search-queries.json), [provider pricing](data/provider-pricing.json).
- [Tokenization observations](results/tokenizer-comparison.json), [verification results](results/verification.json), [source access checks](results/link-checks.json).

No files under `sources/` were modified. No paid API experiments were run. Production claims require the roadmap's realistic traces, pinned models, independent quality labels and invoice reconciliation. The next milestone is a 1,000-unique-task chronological pilot with equal-cache baselines and an explicit quality noninferiority gate.
