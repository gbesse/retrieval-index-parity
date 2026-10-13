#!/usr/bin/env python3
"""Measure judged-result survival between two saved retrieval stages."""

import argparse
import json
import math
import sys
from pathlib import Path

TEXT = {
    "en": {
        "title": "Recall rank survival",
        "invalid": "Invalid rank capture",
        "regression": "Judged retrieval quality decreased",
        "stable": "No measured regression in these judged cases",
        "file": "JSON file with judged before/after rankings",
        "lost": "Relevant results lost from top-k",
        "scope": "Caller-supplied judgments and rankings only. No semantic inference, live model or automatic Hindsight adapter.",
    },
    "fr": {
        "title": "Survie des résultats après reclassement",
        "invalid": "Capture de classement invalide",
        "regression": "La qualité de recherche mesurée a diminué",
        "stable": "Aucune régression mesurée sur ces cas annotés",
        "file": "Fichier JSON des classements avant/après annotés",
        "lost": "Résultats pertinents sortis du top-k",
        "scope": "Annotations et classements fournis par l’appelant uniquement. Aucune inférence sémantique, aucun modèle réel ni adaptateur Hindsight automatique.",
    },
    "es": {
        "title": "Supervivencia de resultados tras reclasificar",
        "invalid": "Captura de clasificación no válida",
        "regression": "La calidad de recuperación medida disminuyó",
        "stable": "Sin regresión medida en estos casos anotados",
        "file": "Archivo JSON de clasificaciones antes/después anotadas",
        "lost": "Resultados relevantes fuera del top-k",
        "scope": "Solo anotaciones y clasificaciones aportadas por quien llama. Sin inferencia semántica, modelo real ni adaptador automático de Hindsight.",
    },
}


def identifiers(value, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        raise ValueError("ids")
    if len(value) > 100_000 or any(
        not isinstance(x, str) or not x.strip() for x in value
    ):
        raise ValueError("ids")
    if len(set(value)) != len(value):
        raise ValueError("duplicate_ids")
    return value


def metrics(ranking, relevant, k):
    ranks = [
        index
        for index, identifier in enumerate(ranking[:k], 1)
        if identifier in relevant
    ]
    dcg = sum(1 / math.log2(rank + 1) for rank in ranks)
    ideal = sum(1 / math.log2(rank + 1) for rank in range(1, min(len(relevant), k) + 1))
    return {
        "recall_at_k": len(ranks) / len(relevant),
        "reciprocal_rank_at_k": 1 / ranks[0] if ranks else 0,
        "ndcg_at_k": dcg / ideal,
        "relevant_in_top_k": len(ranks),
    }


def analyze(capture, lang="en"):
    cases = capture.get("cases") if isinstance(capture, dict) else None
    if not isinstance(cases, list) or not cases or len(cases) > 10_000:
        raise ValueError("cases")
    reports, seen, groups = [], set(), {}
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("case")
        name, language, k = (case.get(key) for key in ("case_id", "language", "k"))
        if not isinstance(name, str) or not name.strip() or name in seen:
            raise ValueError("case_id")
        if not isinstance(language, str) or not language.strip():
            raise ValueError("language")
        if not isinstance(k, int) or isinstance(k, bool) or not 1 <= k <= 10_000:
            raise ValueError("k")
        seen.add(name)
        relevant = set(identifiers(case.get("relevant_ids"), nonempty=True))
        before, after = (identifiers(case.get(key)) for key in ("before", "after"))
        a, b = metrics(before, relevant, k), metrics(after, relevant, k)
        lost = [
            identifier
            for identifier in before[:k]
            if identifier in relevant and identifier not in after[:k]
        ]
        shifts = []
        before_ranks = {identifier: rank for rank, identifier in enumerate(before, 1)}
        after_ranks = {identifier: rank for rank, identifier in enumerate(after, 1)}
        for identifier in sorted(relevant):
            shifts.append(
                {
                    "id": identifier,
                    "before_rank": before_ranks.get(identifier),
                    "after_rank": after_ranks.get(identifier),
                    "lost_from_top_k": identifier in lost,
                }
            )
        decreased = any(
            b[key] < a[key] - 1e-12
            for key in ("recall_at_k", "reciprocal_rank_at_k", "ndcg_at_k")
        )
        report = {
            "case_id": name,
            "language": language,
            "k": k,
            "before": a,
            "after": b,
            "lost_from_top_k": lost,
            "judged_ranks": shifts,
            "regression": decreased,
        }
        reports.append(report)
        groups.setdefault(language, []).append(report)
    by_language = {}
    for language, rows in sorted(groups.items()):
        by_language[language] = {
            "case_count": len(rows),
            "regressed_case_count": sum(r["regression"] for r in rows),
        }
        for stage in ("before", "after"):
            by_language[language][stage] = {
                key: sum(r[stage][key] for r in rows) / len(rows)
                for key in ("recall_at_k", "reciprocal_rank_at_k", "ndcg_at_k")
            }
    regressed = any(r["regression"] for r in reports)
    return {
        "regression": regressed,
        "message": TEXT[lang]["regression" if regressed else "stable"],
        "cases": reports,
        "by_language": by_language,
        "scope": TEXT[lang]["scope"],
    }


def read_capture(path):
    if path.stat().st_size > 10_000_000:
        raise ValueError("size")
    return json.loads(path.read_text(encoding="utf-8"))


HELP = {
    "en": {
        "help": "Show help and exit",
        "usage": "usage",
        "positional": "positional arguments",
        "options": "options",
        "command": "Run a synthetic demo or check saved captures",
        "json": "Print the structured report",
        "language": "Report language",
    },
    "fr": {
        "help": "Afficher l’aide et quitter",
        "usage": "utilisation",
        "positional": "arguments positionnels",
        "options": "options",
        "command": "Exécuter une démo synthétique ou contrôler des captures",
        "json": "Afficher le rapport structuré",
        "language": "Langue du rapport",
    },
    "es": {
        "help": "Mostrar ayuda y salir",
        "usage": "uso",
        "positional": "argumentos posicionales",
        "options": "opciones",
        "command": "Ejecutar una demo sintética o comprobar capturas",
        "json": "Mostrar el informe estructurado",
        "language": "Idioma del informe",
    },
}


def report_language(argv):
    lang = "en"
    for i, value in enumerate(argv):
        if value == "--lang" and i + 1 < len(argv):
            lang = argv[i + 1]
        elif value.startswith("--lang="):
            lang = value.split("=", 1)[1]
    return lang if lang in TEXT else "en"


class Parser(argparse.ArgumentParser):
    def format_help(self):
        return super().format_help().replace("usage:", self.words["usage"] + ":", 1)

    def error(self, message):
        raise ValueError("arguments")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    lang = report_language(argv)
    words = TEXT[lang]
    parser = Parser(description=words["title"], add_help=False)
    parser.words = HELP[lang]
    parser._action_groups[0].title = HELP[lang]["positional"]
    parser._action_groups[1].title = HELP[lang]["options"]
    parser.add_argument("-h", "--help", action="help", help=HELP[lang]["help"])
    parser.add_argument(
        "command", choices=("demo", "check"), help=HELP[lang]["command"]
    )
    parser.add_argument("capture", nargs="?", type=Path, help=words["file"])
    parser.add_argument(
        "--lang", choices=TEXT, default=lang, help=HELP[lang]["language"]
    )
    parser.add_argument("--json", action="store_true", help=HELP[lang]["json"])
    try:
        args = parser.parse_args(argv)
        if args.command == "demo":
            path = (
                Path(__file__).parent / "examples" / "recall-rank" / "multilingual.json"
            )
        elif args.capture:
            path = args.capture
        else:
            raise ValueError("capture")
        report = analyze(read_capture(path), args.lang)
        report["synthetic_demo"] = args.command == "demo"
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(words["title"])
            print(report["message"])
            for row in report["cases"]:
                a, b = row["before"], row["after"]
                print(
                    f"{row['case_id']} [{row['language']}] k={row['k']}: "
                    f"recall {a['recall_at_k']:.3f} → {b['recall_at_k']:.3f}; "
                    f"MRR {a['reciprocal_rank_at_k']:.3f} → {b['reciprocal_rank_at_k']:.3f}; "
                    f"nDCG {a['ndcg_at_k']:.3f} → {b['ndcg_at_k']:.3f}; "
                    f"{words['lost']}: {len(row['lost_from_top_k'])}"
                )
            print(words["scope"])
        if args.command == "demo":
            return 0 if report["regression"] else 1
        return 2 if report["regression"] else 0
    except (OSError, UnicodeError, ValueError, TypeError, RecursionError):
        print(words["invalid"], file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
