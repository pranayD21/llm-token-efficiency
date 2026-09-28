# Literature review

System-level savings depend on the workload, quality threshold, cache state, and cost of deciding when to spend more. Existing methods address most individual mechanisms and several joint systems. The research opportunity is a more demanding evaluation and accounting contract, not the invention of routing plus caching. See the [evidence matrix](04-evidence-matrix.md) for records and limitations.

## Routing, cascading, model mixtures

[FrugalGPT](https://arxiv.org/abs/2305.05176) learns stopping thresholds for sequential model calls and includes earlier calls in expected cost. [RouteLLM](https://arxiv.org/abs/2406.18665) learns strong/weak choice from preferences. [Unified routing and cascading](https://arxiv.org/abs/2410.10347) formalizes sequential choice. These establish that retry-aware model selection is prior work. Preference quality, exact correctness, and recovered performance gaps are different targets; “95% of model quality” does not mean 95% task success.

[RouterBench](https://arxiv.org/abs/2403.12031) makes routing experiments reproducible with precomputed outputs. Its static outcome tables omit live queueing and cache residency. [MixLLM](https://arxiv.org/abs/2502.18482) adds online feedback and latency constraints, so adaptation to changing workloads is also not an empty field. The unresolved operational question is whether calibration survives chronological, session-level changes with complete costs.

[Mixture-of-Agents](https://arxiv.org/abs/2406.04692) spends multiple generations to improve judged quality. Model mixtures can be worthwhile at a high quality threshold, but parallel calls and aggregation context must enter the bill. They should also be compared with a strong single model and a deterministic tool wherever the task permits one.

## Response, semantic, prompt, prefix and KV caches

Exact response caching avoids a model call only when the request identity includes authorization scope, policy/data version, relevant conversation state, and output requirements. Semantic caching adds uncertainty about whether a different request can use the same answer. [MeanCache](https://arxiv.org/abs/2403.02694) already considers user-local privacy and conversational chains. [LaCache](https://arxiv.org/abs/2608.01718) addresses adversarial collisions with query and partial-output matching. Its formal claim must be read within its threat model.

[Online semantic eviction](https://arxiv.org/abs/2508.07675) explicitly prices mismatches and unknown distributions. [FreshCache](https://arxiv.org/abs/2607.04281) studies temporal freshness; hash changes and answer errors have different denominators. [Grounded Cache Routing](https://arxiv.org/abs/2605.27494) shows why safe-hit claims must be reported alongside useful reuse: in one drift table, unsafe-served rate falls from 51.5% to 1.5% while answer hits fall from 56.5% to 2%. This is not evidence of equivalent end-to-end accuracy.

Prefix caches preserve computation over shared beginnings. [CacheBlend](https://arxiv.org/abs/2405.16444) expands reuse to non-prefix chunks with selective recomputation. [Preble](https://arxiv.org/abs/2407.00023) and [CacheRoute](https://arxiv.org/abs/2608.19677) balance cache affinity and load among replicas. Replica placement is distinct from selecting heterogeneous models for semantic quality. A token-count reduction and a cache-compute reduction must not be counted as the same saving twice.

## Context selection, retrieval, compression and memory

[LLMLingua](https://aclanthology.org/2023.emnlp-main.825/) and [LLMLingua-2](https://aclanthology.org/2024.findings-acl.57/) prune prompts; the latter learns token retention through distillation. [RECOMP](https://arxiv.org/abs/2310.04408) compresses retrieved documents and may omit unhelpful augmentation. Retrieval therefore has an upstream indexing/query cost and a downstream context cost. Learned soft prompts and model-internal representations may be compact but require compatible trained models; they are not drop-in text encodings for arbitrary APIs.

[Lost in the Middle](https://arxiv.org/abs/2307.03172) establishes positional sensitivity in evaluated long-context tasks. Keeping more context is not a guarantee of better use. Conversely, average compression quality says little about a rare exception, identifier, or negation that determines a task outcome.

[ACON](https://arxiv.org/abs/2510.00615) jointly compresses observations and history. Its full-text cost analysis explicitly warns that history compression can lose against cache reuse. [Paritok-4B](https://arxiv.org/abs/2608.24188) targets coding-agent spans and identifiers, yet its reported 86.5% retention of single-shot solve quality is a real quality tradeoff. A non-significant test is not proof of equivalence. Memory controllers should retain provenance, distinguish updated tool state from repeated state, and abstain when a hard budget cannot preserve required evidence.

## Reasoning allocation, uncertainty and output length

[Compute-optimal allocation](https://arxiv.org/abs/2408.03314) adapts search and revision to difficulty. [s1](https://arxiv.org/abs/2501.19393) controls a reasoning budget, including spending more for better accuracy. [SelfBudgeter](https://arxiv.org/html/2505.11274v6) learns budgets and improves MATH500 in its reported setting, but loses accuracy on AIME2025. [ESTAR](https://arxiv.org/abs/2602.10004) shortens reasoning while reporting a small absolute accuracy decrease. Calibrate stopping against correctness rather than agreement with the model's own final answer.

[Chain of Draft](https://arxiv.org/html/2502.18600v1) is a particularly useful caution. GPT-4o GSM8K output falls from 205.1 to 43.9 tokens, while accuracy falls from 95.4% to 91.1%. The method can be useful, but a blanket no-loss claim is contradicted by that table. Structured concise outputs, bounded lists, and avoiding regenerated explanations should be evaluated against completeness and format success, not length alone.

## Tokenization, representation, specialization

[Tokens2Words](https://arxiv.org/abs/2410.05864) modifies vocabulary and representations to shorten encoded sequences. Deployment generally cannot change a closed provider's tokenizer. The local tokenizer comparison demonstrates language-dependent counts for the same strings, not quality gains from changing models. JSON minification may save tokens; opaque custom encodings can add decoding mistakes or instructions that erase the gain.

[Distilling Step-by-Step](https://arxiv.org/abs/2305.02301) trains task-specific small models using rationales. [DeepSeek-R1](https://arxiv.org/abs/2501.12948) transfers reasoning into smaller students. These shift cost into teacher generation and training. Break-even volume is setup cost divided by positive per-task savings, and must include quality deterioration and refresh costs. Parameter count alone does not predict generated-token count or API price.

## Inference, batching and agents

[Speculative decoding](https://proceedings.mlr.press/v202/leviathan23a.html) and [EAGLE-3](https://arxiv.org/abs/2503.01840) accelerate accepted generation using drafts and target verification. The intended response length remains. Rejected drafts add work. API discounts cannot be inferred from faster local inference. [PagedAttention](https://arxiv.org/abs/2309.06180) improves KV-memory utilization, and [Sarathi-Serve](https://arxiv.org/abs/2403.02310) reduces prefill/decode interference. Both concern execution capacity under workload and latency conditions.

Batch API discounts trade immediate completion for scheduling flexibility. Grouping similar prefixes can improve reuse, but delayed tasks may violate service objectives. Repeated agent workflows should reuse versioned tool results and count their reinsertion into each later prompt. [AgentPrune](https://arxiv.org/abs/2410.02506) reduces communication edges; [When Agents Coordinate](https://arxiv.org/abs/2608.16801) finds workload-dependent benefits from shared files. Extra agents require a whole-task baseline, including coordinator messages, duplicated reads, and discarded work.

## Joint systems and deployment economics

[AgServe](https://papers.neurips.cc/paper_files/paper/2025/hash/04132e28265a355456f86a1c3fec3bcd-Abstract-Conference.html) is the strongest counterexample to a broad joint-method gap: it combines session-aware KV reuse, model upgrades, retries, and resource allocation. Its ALFWorld table reports quality 90 versus GPT-4o's 94, at 16.5% of cost; “comparable” should not be rewritten as identical. [LLMBridge](https://arxiv.org/abs/2410.11857) combines routing/context/caching, and [TweakLLM](https://arxiv.org/abs/2507.23674) uses cheap rewriting on cache hits. Their existence changes the portfolio toward an auditable benchmark and conservative controllers.

[A Year in LLM Serving](https://arxiv.org/abs/2608.13573) supplies longitudinal production evidence, but its routing comparisons are simulations without task-success labels. Combining such workload realism with objective quality, heterogeneous-model cache economics, and all failed-attempt costs is a research hypothesis supported by the limits of this selected evidence, not a proven global absence.

Current provider documentation is part of the method. The [pricing snapshot](../data/provider-pricing.json) records selected rates and access dates. [OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching) now documents model-generation-specific cache writes and retention; old no-write-fee assumptions cannot be generalized. [Anthropic](https://platform.claude.com/docs/en/about-claude/pricing) distinguishes read/write durations, and [Google](https://ai.google.dev/gemini-api/docs/pricing) includes cache-storage charges. Tool fees, service tiers, regional premiums and long-context thresholds can change the preferred policy even when token counts are identical.
