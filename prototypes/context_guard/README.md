# Context Guard

**ENGINEERING SIMULATION.** Full replay is the primary baseline. The objective is auditable accounting under cache invalidation and rare-fact loss, not a novel compression method. This runnable local prototype measures deterministic retention rules and illustrative token bills. It calls no LLM and provides no evidence about LLM reasoning quality, production latency, or provider savings.

From the repository root:

```sh
.venv/bin/python prototypes/context_guard/benchmark.py
.venv/bin/python -m unittest discover -s prototypes/context_guard -v
```

The only dependency beyond Python's standard library is the root environment's installed `tiktoken`. The accounting module defaults `TIKTOKEN_CACHE_DIR` to the repository's shared `data/tokenizer-cache/`, allowing offline runs with the pre-populated cache. An explicit environment override is respected. The installed tiktoken version is 0.14.0. The prototype's earlier downloaded vocabulary remains in `tokenizer_cache/` as an optional offline fallback; select it with that environment variable if the shared cache is unavailable. Tiktoken verifies the vocabulary's expected SHA-256. No paid API, credentials, external service, or shared accounting interface is needed.

To regenerate the deterministic fixtures or use another configuration:

```sh
.venv/bin/python prototypes/context_guard/fixtures.py
.venv/bin/python prototypes/context_guard/benchmark.py --config prototypes/context_guard/config.json --output prototypes/context_guard/results
```

All output paths must stay inside this directory. `results/results.json` contains configuration, fixture hashes, run summaries, and local timings. `results/requests.jsonl` contains every actual serialized request, retained record IDs, reader answer, gold, decision, token bill, and failure reason. The default run has 172 trajectory runs and 2,064 requests: seven context policies, four scenarios, a default budget plus five sweep budgets, and one exact-local reference run per scenario. Default and sweep runs are tagged separately, including the deliberately repeated 1,100-token point.

## Architecture

`sample.jsonl` contains 12 observation turns per scenario, public deployment intent, monotonically increasing record sequence IDs, simulation time, explicit facts, protection flags, and tool resource/version metadata. `evaluation.jsonl` holds the questions and gold answers separately. `fixtures.py` creates both files; the controller never imports it or reads evaluation data.

`controller.py` receives only its previously retained events, new observations, public intent, a numeric capacity, and the cache estimator. Selection is online and irreversible. Evicted records cannot be fetched from the full source history. The harness reserves space for the current question and output before selection. The controller sees the reserve size but not question content or gold. It ranks against the fixed public intent, so future rare questions cannot steer retention.

`reader.py` parses the actual serialized request and looks up each requested fact. For a tool resource it uses the highest retained version, even if a lower version arrived later. Conflicting values at the same version and missing facts produce `null`. Identifiers remain exact strings. No policy name, success probability, gold answer, or external memory is available to the reader. The harness compares its answer with gold only after reading.

The exact-local reference has zero controller overhead by construction and zero simulated API cost. Its reader time is actually measured. It bypasses the simulated model context limit because it is local code operating on complete structured observations. It does not read gold; corrupting an observed identifier changes its answer and causes a failure. Its serialized token counts are diagnostic, while billed input/output counts are zero. This is a reference for problems solvable directly from structured data, not a model-performance baseline.

The history is an observation/event log with prior assistant outputs. Each request contains a stable system record, retained events in sequence order, and the current evaluation question. Prior evaluation questions are probes and are not replayed. Prior generated outputs are replayed as opaque assistant text and are not authoritative facts. Thus “full replay” here means the full event/output log, not a general chat transcript simulator. Every replayed byte is charged again as input, with any eligible cache discount.

## Policies

| Name | Rule |
| --- | --- |
| `exact_local` | Reference solver with complete observation/output history, the same deterministic reader, no controller, and no simulated API calls. Runs once per scenario, outside the budget sweep. |
| `full` | Replay the complete event/output history. Reject requests that exceed the configured context budget. |
| `recency` | Keep a contiguous suffix of whole records that fits. Stop at the first record that cannot fit. |
| `relevance` | Greedily select by lexical overlap with public intent, breaking ties by recency. No protection or deduplication. |
| `guard` | Preserve explicitly protected records, remove obsolete tool versions and exact repeated snapshots, then prioritize fact records, lexical overlap, and recency. Compact toward 65% of available event capacity. |
| `guard_no_gate` | Same guard selection, with proactive compaction even when rewriting the prefix costs more. |
| `guard_no_protection` | Guard with protection disabled. |
| `guard_no_dedup` | Guard with tool deduplication disabled. |

Version deduplication uses `(resource, version, facts)`. It retains all distinct payloads at the maximum observed retained version so conflicting same-version facts cause abstention. Repeated identical snapshots keep their earliest position. The assumption is that each version is a complete fact snapshot for that resource; partial updates would require a different merge rule. Protection applies to retained maximum-version records after deduplication. There is no separate permanent version registry once every snapshot of a resource has been evicted.

The cache gate compares the estimated **current input cost** of the raw event prefix and compacted prefix. When the raw prefix fits and costs no more, it defers compaction. It never overrides the hard budget. Output and question costs are treated as equal for this estimate; billing uses the exact complete request afterward. Token boundary effects and later requests can make the estimate imperfect. There is no future-workload oracle or claim that the gate minimizes trajectory cost.

## Accounting

The budget includes serialized input plus a 96-token output reserve. A two-token boundary margin is deducted during selection; the final request is tokenized again and checked. Protected facts that cannot fit cause explicit rejection, rather than silent constraint loss. A malformed custom fixture whose actual output exceeds its reserve raises an error.

`accounting.py` uses `cl100k_base` on the entire newline-delimited, sorted-key JSON input. Outputs are separately serialized and tokenized. This serialization is the simulation's wire format; it does not estimate vendor chat framing.

The cache stores only the previous submitted input. A hit is its longest common token prefix with the new input, rounded down to whole configurable blocks, subject to a minimum prefix and TTL. Defaults are 64-token blocks, 128-token minimum, and three simulated time units. TTL is inclusive at the boundary and refreshes on submission. A five-unit gap before turn 9 exercises expiration. Estimating cost does not update the cache. Rejected requests neither incur charges nor replace the cache. Compaction preserves only the actual unchanged prefix, often the system record; later matching spans receive no cache credit.

Illustrative USD rates per million tokens are input $2, output $8, and cache read $0.20:

```text
uncached = input_tokens - cached_tokens
cost = (uncached * 2 + cached_tokens * 0.20 + output_tokens * 8) / 1,000,000
```

Cached and uncached input partitions never overlap. Each generated output is charged once as output on its originating request and, when retained, as input on subsequent requests. There is no generative compressor and no compressor token fee. Its real CPU overhead is measured separately with a monotonic clock.

`cost_per_success_usd` is total trajectory cost divided by correctly answered requests, including spending on incorrect submitted answers. With zero successes it is JSON `null`. `trajectory_success` requires every turn correct; `cost_per_successful_trajectory_usd` is null unless the entire trajectory succeeds. Rejected requests have zero simulated cost, so a cheap full-replay run with many rejections is not an economical successful trajectory.

## Scenarios and limits

- `standard` asks routine status questions, later checks the current endpoint, and finally asks for early protected routing facts.
- `rare` also asks for an early unprotected audit identifier at the final turn. Under tighter budgets, even the guard loses it. Protection depends on supplied metadata.
- `stale` publishes version 2, then delivers only delayed version-1 responses from turn 7 onward. Selection must preserve the newer state despite recent obsolete evidence.
- `budget-too-small` uses 100 tokens by default, below the system/question/output requirements. Every context policy rejects all requests; the exact-local reference does not use the simulated model budget. The sweep gives the same observations larger budgets.

Sweeps use 180, 450, 1,100, 2,400, and 8,000 tokens. They include empty-answer failures, protected-fact overflow, lost rare facts, wrong stale endpoints, and sufficient space for full replay. The unit tests cover these mechanisms, exact token billing, TTL/block boundaries, cache invalidation, gate economics, same-version conflicts, resource isolation, irreversible eviction, and gold isolation.

These are four hand-authored synthetic trajectories without statistical independence, learned compression, model calls, or natural-language fact extraction. The reader cannot be distracted and accepts structured facts as authoritative. Whole-record selection may waste budget, the guard relies on annotation quality, and dropping an unprotected fact can be irreversible. Local timings include Python selection and tokenization; they exclude model latency, tokenizer initialization, and result-file writes. They vary by machine and run. Only non-timing behavior is deterministic.

## Research inspiration

[ACON, Appendix A](https://arxiv.org/html/2510.00615v1) discusses history compression invalidating KV caches and requiring recomputation. That motivates testing the compaction gate. This prototype models an illustrative prefix billing cache, not ACON's implementation or transformer KV memory behavior.

[Paritok-4B](https://arxiv.org/abs/2608.24188) reports imperfect identifier fidelity and uses extractive compression. Its 96.0% figure describes identifiers, paths, and numbers emitted that also appear in the input; it is not a guarantee that every needed identifier survives. This prototype therefore checks exact strings and missing facts directly. Neither paper's empirical performance is transferred to these simulation results.
