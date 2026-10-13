# retrieval-index-parity

## New: do relevant memories survive reranking?

`python3 recall_rank.py demo --lang en` shows a **synthetic** multilingual control: three judged IDs stay in the top 12 for FR/EN/ES, but move from ranks 1/2/3 to 70/74/71 for one Chinese case. The shape is inspired by [Hindsight #5519](https://github.com/vectorize-io/hindsight/issues/5519), not measured by this tool on Hindsight. Unlike answer-level evaluation in [Ragas](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_recall/), this checks exact judged IDs between two captured ranking stages without a judge model.

```sh
python3 recall_rank.py check examples/recall-rank/multilingual.json --lang en --json
```

Input: `{ "cases": [{ "case_id": "example", "language": "en", "k": 12, "relevant_ids": ["a"], "before": ["a", "b"], "after": ["b", "a"] }] }`. Arrays are complete ordered captures of the supplied stage, using stable IDs, not scores. IDs in each array and case IDs must be unique; relevance judgments must be explicit and nonempty. `k` is 1–10000. Empty rankings are allowed. A relevant ID absent from a stage has `null` rank, not zero. The report lists lost top-k IDs, exact ranks, Recall@k, reciprocal rank at k and binary nDCG@k. Per-language values are arithmetic means across cases, so a language regression stays visible. Any decrease in one of these three metrics fails the gate, including a drop within top-k; this strict policy deliberately does not trade a worse first result against a better recall.

Exit codes: **0** no measured regression, **2** regression, **1** invalid input. Demo exits 0 when the expected regression is found. Python 3.11+, no dependency or network. Saved JSON is limited to 10 MB. No query or document text is printed; case and judged document IDs appear in reports. Ground truth is supplied by you: incomplete labels can produce misleading metrics. This is no automatic Hindsight adapter, no semantic relevance estimator and no proof of multilingual model quality. FR/EN/ES changes only the report language; Chinese metadata and user content remain unchanged.

## New: is my BM25 index actually used?

`python3 bm25_plan.py demo --lang en` shows a plan that misses the expected index followed by one that uses it. The captures are **reconstructed** from [Hindsight #5408](https://github.com/vectorize-io/hindsight/issues/5408); displayed timings are not benchmarks run by this tool. For a real `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` capture of a SELECT query you control:

```sh
python3 bm25_plan.py check plan.json --index idx_memory_units_text_search --catalog indexes.json --lang en
```

`indexes.json` is a JSON array of index names or `pg_indexes` rows with `indexname`. Without that catalog, the tool only observes that the index did not appear in the execution; it cannot prove the index exists. Exit codes: 0 used, 2 not used, 3 incomplete capture or index absent from catalog, 1 invalid input. It does not connect to PostgreSQL or print query text. A plan alone cannot explain _why_ the planner chose another path.

**Related projects:** [Hindsight](https://github.com/vectorize-io/hindsight) uses BM25 retrieval in this case; [VectorChord BM25](https://github.com/supervc-stack/VectorChord-bm25) supplies the index. This independent checker reads exported plans, with no direct integration or affiliation.

## New: Leviathan group boundary

`python3 tenant_scope.py tenant-demo --lang en` shows another customer's result in strict search (successful demo exits 0). For real `leviathan --json search` output run `python3 tenant_scope.py check search.json --leviathan --group customer-a --policy strict --lang en`. Policy `labeled_fallback` allows `other_groups` only when each card has `other_group: true`. Without `--leviathan`, the normalized format is `{requested_group, policy, results:[{group,label}]}`. This checks a capture, not upstream ACLs; documented fallback is not by itself evidence of a leak.

**Related project:** [Leviathan](https://github.com/elstongun/leviathan) exposes an explicit `OTHER CUSTOMER` fallback. This command reads its JSON output, without affiliation or a Leviathan patch.

Checks IDs, hashes and ACLs across source, FTS5 and vector metadata.

[Français](README.md) · [English](README.en.md) · [Español](README.es.md)

## Related projects

- [sqlite-fts5-check — internal FTS5 drift](https://github.com/agentscope-ai-java/sqlite-fts5-check)
- [rag-staleness-check — stale documents in indexes](https://pypi.org/project/rag-staleness-check/)
- [Truffler — hybrid retrieval with labels](https://github.com/kieranklaassen/truffler)

These projects document the need or cover part of the problem. No affiliation or integration with them is claimed.

## Quick start

```bash
python3 tool.py demo
python3 tool.py check examples/healthy.sql
```

Python 3.11+; no external package required. / Python 3.11+ ; aucune dépendance externe. / Python 3.11+; sin dependencias externas.

## Current scope

The SQLite comparator checks active IDs, tombstones, hashes and ACLs across source, FTS and vector metadata, plus FTS5 retrieval by a probe term. It does not yet search a real vector index.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT.
