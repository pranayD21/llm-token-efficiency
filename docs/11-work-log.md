# Work log

All work began on 2026-09-06 PDT. Phase order was tooling/discovery, targeted verification, portfolio selection, implementation, evaluation, and reconciliation. Research and prototype construction overlapped where evidence was sufficient. The log records concise decisions and executed checks, not private reasoning traces.

1. Read `/Users/pranaydogra/.codex/AGENTS.md` and the project `AGENTS.md`, plus relevant skill instructions. No nested instructions existed before new files. Verified `sources/` was empty. Created new work only outside it.
2. Inspected tool metadata and local programs. Found Python 3.14.7, git, system curl; no preinstalled tiktoken, numpy, pytest or pypdf in the default Python. `uv` and `pdftotext` were not found. Native subagents were available; no `update_plan` or plugin-search/suggest tools were exposed.
3. Used Plugin Management dependency and permission reads for Consensus. It was available but not installed. Existing public research access was sufficient; no external plugin was selected or claimed installed.
4. Initial Python HTTP calls failed on sandbox DNS. Approved network access then failed Python certificate verification. System curl and pip with system CA certificates worked. TLS verification remained enabled.
5. Created `.venv`; installed pinned tiktoken 0.14.0 and pypdf 6.0.0 using binary wheels. Saved installation report, frozen versions, hashes and `pip check` outcome. Downloaded and used cl100k/o200k vocabularies. Counted multilingual strings. Extracted LLMLingua-2 and AgServe PDFs.
6. Used OpenAlex for paper discovery; rejected unrelated Crossref title results and verified exact ACL DOI instead. Conducted two parallel primary-source research streams for routing and inference/reasoning. Coordinator verified cache/context literature, provider policies and high-impact counterexamples.
7. Corrected an informal ACON identifier. Excluded browser-challenged vCache from numerical synthesis. Inspected ACON's cache-cost limitation and AgServe's combined cache/cascade architecture. Read actual table values rather than treating “comparable” as equal quality. Built 39 deduplicated research records and bibliography.
8. Selected Ledger Router and Context Guard for auditable engineering/evaluation value. Deferred learned reasoning and GPU-serving projects pending realistic model infrastructure. Read-only sources were never changed.
9. Built router/accounting locally; delegated Context Guard in its own directory. Added deterministic readers/engines, configs, sample workloads, baselines, ablations, tests and ledgers. Both include exact-local references to expose when no LLM is needed.
10. Initial unsafe-cache test found no collision because tenant assignment remained tied to amount parity. Fixed the fixture to repeat amounts across different tenants. This was a benchmark defect, not evidence of safe semantic caching.
11. Independent router review found experiment-label leakage, a partially warm “cold” workload, misleading ablation names, unequal-cache baselines, incorrect fallback-probability estimation, wording-cache interaction, confounded drift, and acceptance of nonfinite charges. Fixed all eight. Added regression tests, equal-cache fixed baselines, separately calibrated rejection rates, independent wording drift and a known silent verifier error.
12. Added billed transient failure attempts and retries, plus a uniform explicitly charged prefix warm-up in the affinity workload. The core policy no longer branches on scenario labels. Fully cold spacing now exceeds both TTLs. Early cold-cost conclusions were discarded and results regenerated.
13. The initial citation checker assumed UTF-8 for PDF responses and failed. Fixed response decoding, preserving explicit blocked/error results. The first offline link pass also correctly flagged its not-yet-written reports; generated the reports and reran.
14. Ran the complete benchmarks and tests, threshold/verifier-price sensitivity, counterfactual calibration cost, and independent per-record reconciliation. Final reported metrics come from saved artifacts, not earlier intermediate runs. Checked citation identities, local links and required file contents. Online URL outcomes are recorded separately; a challenge or timeout is not evidence of a nonexistent paper.

## Reproduction commands

From the repository root, after creating an isolated environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --only-binary=:all: -r requirements.lock
.venv/bin/python -m pip check
.venv/bin/python -m unittest discover -s prototypes/ledger_router -p 'test_*.py'
.venv/bin/python -m unittest discover -s prototypes/context_guard -v
.venv/bin/python prototypes/ledger_router/benchmark.py
.venv/bin/python prototypes/ledger_router/sensitivity.py
.venv/bin/python prototypes/context_guard/benchmark.py
.venv/bin/python scripts/build_results_report.py
.venv/bin/python scripts/verify_repository.py
```

The reviewed macOS wheel hashes are in `requirements-hashed.txt`; use `pip install --require-hashes -r requirements-hashed.txt` on the matching platform. First-run vocabulary downloads require HTTPS unless the included caches are retained. This environment used `--cert /etc/ssl/cert.pem` for installation. Routine benchmark runs are offline.

Research-data rebuild, with network access when refreshing pages:

```sh
.venv/bin/python scripts/fetch_sources.py
.venv/bin/python scripts/build_literature.py
.venv/bin/python scripts/build_tables.py
.venv/bin/python scripts/check_links.py
```

`fetch_sources.py` refreshes the core sources; the complete set of canonical paper URLs remains in `data/literature.json`. Regeneration uses archived primary metadata for the additional routing/inference records. Refreshing sources can change metadata after the cutoff; preserve the archived date-specific dataset for reproducibility.

## Evidence of execution

[Environment/version report](../results/environment.json), [install report](../data/raw/install-report.json), [router run](../results/router-run.log), [context test log](../results/context-tests.log), [context run](../results/context-run.log), [verification](../results/verification.json), and [URL outcomes](../results/link-checks.json).

No paid model calls, external messages, repository publishing, deployment or global package changes occurred. Production quality and provider invoice validation remain future work under the [roadmap](08-implementation-roadmap.md).

Final audit: 31 tests passed. All 39 included primary-source URLs were accessible in the final HTTP check; 65 of 68 total cited URLs were directly accessible. Three tooling-help pages returned HTTP 403 to curl after being available through the web tool. They support rejected-tool audit notes, not research results. Their access limitation is retained in the ledger. The separate vCache candidate remains excluded.

Independent follow-up review found no new simulation correctness blockers and replayed all 20,160 router policy-request combinations. A final Markdown table check found and corrected one separator-column mismatch. Cumulative context compression ratios were added to the generated results report.
