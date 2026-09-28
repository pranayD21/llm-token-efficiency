# Token efficiency research and engineering report

Audience: LLM platform engineers and research leads. Cutoff: 2026-09-06 PDT.

The strongest supported direction is a quality-constrained, auditable cost benchmark for interactions between routing, caches, retries, context selection and drift. Existing systems already combine several of these mechanisms. The selected implementations are local experiments with deterministic model behavior; they do not establish production LLM savings.

This canonical report is organized into maintained chapters: [scope](00-scope-and-definitions.md), [search method](02-search-protocol.md), [evidence synthesis](03-literature-review.md), [matrix](04-evidence-matrix.md), [gaps](05-literature-gaps.md), [selection](06-project-portfolio.md), [implemented projects](07-selected-projects.md), [results](09-experiments-and-results.md), and [limitations](10-risks-limitations-and-open-questions.md). The separate [claim ledger](../data/claim-to-source.json) connects reported findings to primary metadata and distinguishes reviewer interpretation.

The local results support conditional engineering value: the context gate improves one fixture at equal quality, while the router's cheaper default trades accuracy and can regress under drift. Release requires a chronological real-model pilot with equal-cache baselines and independent success labels, as specified in the [roadmap](08-implementation-roadmap.md).
