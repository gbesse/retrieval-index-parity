#!/usr/bin/env python3
"""Check normalized or Leviathan JSON search results against a tenant boundary."""

import argparse
import json
import sys
from pathlib import Path

TEXT = {
    "en": ("Tenant search boundary", "outside requested group", "boundary respected"),
    "fr": ("Frontière de recherche client", "hors du groupe demandé", "frontière respectée"),
    "es": ("Límite de búsqueda por cliente", "fuera del grupo solicitado", "límite respetado"),
}


def audit(data):
    requested = data["requested_group"]
    policy = data["policy"]
    if not isinstance(requested, str) or not requested or policy not in ("strict", "labeled_fallback"):
        raise ValueError("requested_group and policy strict/labeled_fallback are required")
    findings = []
    for index, result in enumerate(data["results"], 1):
        if result["group"] == requested:
            continue
        if policy == "strict":
            findings.append({"result": index, "kind": "cross_group"})
        elif result.get("label") != "OTHER CUSTOMER":
            findings.append({"result": index, "kind": "unlabeled_fallback"})
    return {"ok": not findings, "requested_group": requested, "policy": policy,
            "results": len(data["results"]), "findings": findings}


def audit_leviathan(outcome, requested_group, policy):
    """Read SearchOutcome from `leviathan --json search`, preserving its fallback marker."""
    if not requested_group or policy not in ("strict", "labeled_fallback"):
        raise ValueError("group and policy strict/labeled_fallback are required")
    if not isinstance(outcome.get("results"), list):
        raise ValueError("Leviathan SearchOutcome.results must be an array")
    primary = outcome["results"]
    other = outcome.get("other_groups", [])
    if not isinstance(other, list):
        raise ValueError("Leviathan SearchOutcome.other_groups must be an array")
    normalized = []
    for card in primary:
        normalized.append({"group": card.get("group"),
                           "label": "OTHER CUSTOMER" if card.get("other_group") is True else None})
    for card in other:
        normalized.append({"group": card.get("group"),
                           "label": "OTHER CUSTOMER" if card.get("other_group") is True else None})
    report = audit({"requested_group": requested_group, "policy": policy,
                    "results": normalized})
    report["format"] = "leviathan_search_outcome"
    report["fallback_results"] = len(other)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=("tenant-demo", "check"))
    ap.add_argument("input", type=Path, nargs="?")
    ap.add_argument("--leviathan", action="store_true", help="parse Leviathan --json search output")
    ap.add_argument("--group", help="requested group for --leviathan")
    ap.add_argument("--policy", choices=("strict", "labeled_fallback"), default="strict")
    ap.add_argument("--lang", choices=TEXT, default="en")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.command == "tenant-demo":
            data = {"requested_group": "customer-a", "policy": "strict",
                    "results": [{"id": "ticket-2", "group": "customer-b",
                                 "label": "OTHER CUSTOMER"}]}
        else:
            if not args.input:
                ap.error("check requires INPUT.json")
            data = json.loads(args.input.read_text())
        result = audit_leviathan(data, args.group, args.policy) if args.leviathan else audit(data)
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        title, bad, good = TEXT[args.lang]
        print(title)
        print(good if result["ok"] else f"{len(result['findings'])} {bad}")
    if args.command == "tenant-demo":
        return 0 if not result["ok"] else 1
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
