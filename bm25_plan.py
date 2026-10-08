#!/usr/bin/env python3
"""Check whether an expected PostgreSQL BM25 index was used in an EXPLAIN capture."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TEXT = {
    "en": {
        "title": "BM25 plan check",
        "used": "Expected index used in the captured execution",
        "missing": "Expected index not used in the captured execution",
        "unknown": "Execution or index evidence is incomplete",
        "elapsed": "Execution time",
        "catalog": "Index existence confirmed by supplied catalog",
        "unverified": "Index existence not verified; the plan alone cannot prove it exists",
        "absent": "Expected index is absent from the supplied catalog",
        "invalid": "Invalid plan or catalog",
    },
    "fr": {
        "title": "Contrôle du plan BM25",
        "used": "Index attendu utilisé dans l’exécution capturée",
        "missing": "Index attendu non utilisé dans l’exécution capturée",
        "unknown": "Preuve d’exécution ou d’index incomplète",
        "elapsed": "Temps d’exécution",
        "catalog": "Existence de l’index confirmée par le catalogue fourni",
        "unverified": "Existence de l’index non vérifiée ; le plan seul ne la prouve pas",
        "absent": "Index attendu absent du catalogue fourni",
        "invalid": "Plan ou catalogue invalide",
    },
    "es": {
        "title": "Comprobación del plan BM25",
        "used": "Índice esperado utilizado en la ejecución capturada",
        "missing": "Índice esperado no utilizado en la ejecución capturada",
        "unknown": "Prueba de ejecución o del índice incompleta",
        "elapsed": "Tiempo de ejecución",
        "catalog": "Existencia del índice confirmada por el catálogo aportado",
        "unverified": "Existencia del índice no verificada; el plan por sí solo no la demuestra",
        "absent": "Índice esperado ausente del catálogo aportado",
        "invalid": "Plan o catálogo no válido",
    },
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def index_catalog(value):
    """Accept a JSON array of pg_indexes rows or index names."""
    if isinstance(value, dict):
        value = value.get("indexes")
    if not isinstance(value, list):
        raise ValueError("catalog_shape")
    names = set()
    for row in value:
        name = row if isinstance(row, str) else row.get("indexname") if isinstance(row, dict) else None
        if not isinstance(name, str) or not name:
            raise ValueError("catalog_entry")
        names.add(name)
    return names


def captured_plan(value):
    if isinstance(value, list):
        if len(value) != 1:
            raise ValueError("plan_count")
        value = value[0]
    if not isinstance(value, dict) or not isinstance(value.get("Plan"), dict):
        raise ValueError("plan_shape")
    return value


def walk(node):
    if not isinstance(node, dict):
        raise ValueError("plan_node")
    yield node
    children = node.get("Plans", [])
    if not isinstance(children, list):
        raise ValueError("plan_children")
    for child in children:
        yield from walk(child)


def analyze(plan, expected_index: str, catalog=None):
    if not expected_index:
        raise ValueError("index_required")
    capture = captured_plan(plan)
    nodes = list(walk(capture["Plan"]))
    elapsed = capture.get("Execution Time")
    has_execution = isinstance(elapsed, (int, float)) and not isinstance(elapsed, bool) and elapsed >= 0
    loops = capture["Plan"].get("Actual Loops")
    has_execution = has_execution and isinstance(loops, (int, float)) and not isinstance(loops, bool) and loops > 0
    used = sorted({node["Index Name"] for node in nodes
                   if isinstance(node.get("Index Name"), str)
                   and isinstance(node.get("Actual Loops"), (int, float))
                   and not isinstance(node["Actual Loops"], bool)
                   and node["Actual Loops"] > 0})
    all_plan_indexes = sorted({node["Index Name"] for node in nodes
                               if isinstance(node.get("Index Name"), str)})
    present = None if catalog is None else expected_index in index_catalog(catalog)
    if not has_execution or present is False:
        status = "inconclusive"
    else:
        status = "used" if expected_index in used else "not_used"
    return {
        "status": status,
        "expected_index": expected_index,
        "catalog_confirms_index": present,
        "execution_time_ms": elapsed if has_execution else None,
        "used_indexes": used,
        "planned_indexes": all_plan_indexes,
        "note": "Only the supplied EXPLAIN ANALYZE execution is checked; index existence needs a catalog capture.",
    }


def render(report, lang):
    words = TEXT[lang]
    status_key = {"used": "used", "not_used": "missing", "inconclusive": "unknown"}[report["status"]]
    lines = [words["title"], words[status_key]]
    if report["execution_time_ms"] is not None:
        lines.append(f"{words['elapsed']}: {report['execution_time_ms']:g} ms")
    presence = report["catalog_confirms_index"]
    lines.append(words["catalog"] if presence is True else words["absent"] if presence is False else words["unverified"])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("demo", "check"))
    parser.add_argument("plan", nargs="?", type=Path)
    parser.add_argument("--index", default="idx_memory_units_text_search")
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--lang", choices=TEXT, default="en")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            base = Path(__file__).parent / "examples" / "bm25"
            catalog = read_json(base / "catalog.json")
            reports = [analyze(read_json(base / name), args.index, catalog)
                       for name in ("slow-plan.json", "indexed-plan.json")]
            success = [row["status"] for row in reports] == ["not_used", "used"]
            if args.json:
                print(json.dumps({"reconstructed_demo": True, "reports": reports}, ensure_ascii=False, indent=2))
            else:
                for row in reports:
                    print(render(row, args.lang), end="\n\n")
            return 0 if success else 1
        if args.plan is None:
            print(TEXT[args.lang]["invalid"], file=sys.stderr)
            return 1
        catalog = read_json(args.catalog) if args.catalog else None
        report = analyze(read_json(args.plan), args.index, catalog)
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        print(TEXT[args.lang]["invalid"], file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render(report, args.lang))
    return {"used": 0, "not_used": 2, "inconclusive": 3}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
