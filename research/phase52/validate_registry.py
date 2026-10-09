#!/usr/bin/env python3
"""Validate Phase 52 registries and emit deterministic, resumable config shards.

This script enumerates configurations only. It does not claim to backtest them.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "research" / "phase52" / "strategy_registry.csv"
SPACE = ROOT / "research" / "phase52" / "configuration_space.json"


def read_inputs() -> tuple[list[dict[str, str]], dict[str, Any]]:
    with REGISTRY.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    with SPACE.open(encoding="utf-8") as fh:
        space = json.load(fh)
    return rows, space


def validate(rows: list[dict[str, str]], space: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "candidate_id", "family_id", "family_name", "selector_mode",
        "selector_definition", "risk_class", "source_lineage", "rule_summary",
        "initial_state",
    }
    if not rows:
        return ["registry contains no candidate rows"]
    missing = required.difference(rows[0].keys())
    if missing:
        errors.append("missing registry columns: " + ", ".join(sorted(missing)))
    ids = [r.get("candidate_id", "") for r in rows]
    if len(ids) != len(set(ids)):
        errors.append("duplicate candidate_id values")
    if any(not value.strip() for value in ids):
        errors.append("blank candidate_id")
    families = {r.get("family_id", "") for r in rows}
    modes = {r.get("selector_mode", "") for r in rows}
    if len(rows) != len(families) * len(modes):
        errors.append(f"registry is not a complete family × selector matrix: rows={len(rows)}, families={len(families)}, modes={len(modes)}")
    if len(rows) < 300:
        errors.append(f"candidate hypothesis count {len(rows)} is below the target of 300")
    if set(space.get("family_to_group", {})) != families:
        errors.append("family_to_group keys do not exactly match the registry family_id set")
    if set(space.get("selector_domains", {})) != modes:
        errors.append("selector_domains keys do not exactly match the registry selector_mode set")
    known_dims = set(space.get("general_domains", {}))
    known_dims.update({"strike_selection"})
    for group, dims in space.get("parameter_groups", {}).items():
        unknown = set(dims) - known_dims
        if unknown:
            errors.append(f"parameter group {group} contains unknown dimensions: {sorted(unknown)}")
    for fam, group in space.get("family_to_group", {}).items():
        if group not in space.get("parameter_groups", {}):
            errors.append(f"family {fam} points to missing parameter group {group}")
    for mode, dims in space.get("selector_domains", {}).items():
        for dim in dims:
            if dim not in known_dims:
                errors.append(f"selector {mode} contains unknown dimension {dim}")
    for dim, branches in space.get("conditional_dimensions", {}).items():
        if dim not in known_dims:
            errors.append(f"conditional dimension key {dim} is undeclared")
        if not isinstance(branches, dict) or not branches:
            errors.append(f"conditional dimension {dim} has no branches")
        else:
            for branch_name, values in branches.items():
                if not isinstance(values, dict) or not values:
                    errors.append(f"conditional dimension {dim}/{branch_name} is empty")
                for child, child_values in values.items():
                    if child not in known_dims or not child_values:
                        errors.append(f"invalid conditional child domain {dim}/{branch_name}/{child}")
    for row in rows:
        for field in ("family_name", "selector_definition", "risk_class", "source_lineage", "rule_summary", "initial_state"):
            if not row.get(field, "").strip():
                errors.append(f"{row.get('candidate_id', '?')} has blank {field}")
        if row.get("selector_mode") == "BASELINE" and space.get("selector_domains", {}).get("BASELINE"):
            errors.append("BASELINE selector must not have factor-threshold dimensions")
            break
    cost = space.get("cost_model", {})
    if cost.get("broker") != "Paytm Money":
        errors.append("broker cost model must specify Paytm Money")
    if not cost.get("evaluate_all_scenarios_for_every_configuration", False):
        errors.append("cost scenarios must be evaluated for every config rather than searched as a profitable parameter")
    for name, values in space.get("general_domains", {}).items():
        if not isinstance(values, list) or not values:
            errors.append(f"general domain {name} is not a non-empty list")
    return errors


def dimensions_for(row: dict[str, str], space: dict[str, Any]) -> list[tuple[str, list[Any]]]:
    group = space["family_to_group"][row["family_id"]]
    base_names = space["parameter_groups"][group]
    selector_names = space["selector_domains"][row["selector_mode"]]
    all_names: list[str] = []
    for name in list(base_names) + list(selector_names):
        if name not in all_names:
            all_names.append(name)
    selection_branches = space["conditional_dimensions"]["strike_selection"]
    branches: list[tuple[str, list[Any]]] = []
    for selection, child_map in selection_branches.items():
        names = [n for n in all_names if n != "strike_selection" and n not in {k for ch in selection_branches.values() for k in ch}]
        names.append("strike_selection")
        for child_name, child_values in child_map.items():
            if child_name in all_names:
                names.append(child_name)
        dims = [(n, [selection] if n == "strike_selection" else (child_map.get(n, {}).get("values") if False else space["general_domains"][n])) for n in names]
        # The selected strike branch exposes only its applicable child dimension.
        for child_name in {k for ch in selection_branches.values() for k in ch}:
            if child_name not in child_map:
                dims = [(n, vals) for n, vals in dims if n != child_name]
        branches.append((selection, dims))
    # Selector thresholds are only present for the selected router, never for BASELINE.
    return [dims for _, dims in branches]


def product_size(dimensions: list[tuple[str, list[Any]]]) -> int:
    size = 1
    for _, values in dimensions:
        size *= len(values)
    return size


def unrank_product(dimensions: list[tuple[str, list[Any]]], index: int) -> dict[str, Any]:
    total = product_size(dimensions)
    if index < 0 or index >= total:
        raise IndexError(f"product index {index} outside [0,{total})")
    result: dict[str, Any] = {}
    remainder = index
    digits = [0] * len(dimensions)
    for i in range(len(dimensions) - 1, -1, -1):
        base = len(dimensions[i][1])
        digits[i] = remainder % base
        remainder //= base
    for (name, values), digit in zip(dimensions, digits):
        result[name] = values[digit]
    return result


def branches_for(row: dict[str, str], space: dict[str, Any]) -> list[list[tuple[str, list[Any]]]]:
    group = space["family_to_group"][row["family_id"]]
    names: list[str] = []
    for name in list(space["parameter_groups"][group]) + list(space["selector_domains"][row["selector_mode"]]):
        if name not in names:
            names.append(name)
    all_conditional_children = {child for m in space["conditional_dimensions"]["strike_selection"].values() for child in m}
    names = [n for n in names if n not in all_conditional_children and n != "strike_selection"]
    # Cost scenarios are outputs for each replay, not separate search configurations.
    names = [n for n in names if n != "cost_scenarios"]
    base = [(n, space["general_domains"][n]) for n in names]
    answer = []
    for selection, child_map in space["conditional_dimensions"]["strike_selection"].items():
        dims = list(base)
        dims.append(("strike_selection", [selection]))
        for child_name, child_values in child_map[selection].items() if False else child_map.items():
            if child_name in space["general_domains"]:
                dims.append((child_name, child_values))
        answer.append(dims)
    return answer


def candidate_size(row: dict[str, str], space: dict[str, Any]) -> int:
    return sum(product_size(d) for d in branches_for(row, space))


def config_id(grid_version: str, candidate_id: str, config: dict[str, Any]) -> str:
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    key = grid_version + "|" + candidate_id + "|" + canonical
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]


def audit(rows: list[dict[str, str]], space: dict[str, Any]) -> dict[str, Any]:
    per_mode = {}
    total = 0
    per_family_group = {}
    for r in rows:
        n = candidate_size(r, space)
        per_mode[r["selector_mode"]] = per_mode.get(r["selector_mode"], 0) + n
        per_family_group[r["family_id"]] = per_family_group.get(r["family_id"], 0) + n
        total += n
    return {
        "grid_version": space["grid_version"],
        "status": "CONFIGURATION_ENUMERATION_ONLY_NO_BACKTEST_RESULTS",
        "candidate_hypotheses": len(rows),
        "structure_families": len({r["family_id"] for r in rows}),
        "selector_modes": len({r["selector_mode"] for r in rows}),
        "configuration_count": total,
        "configurations_by_selector_mode": per_mode,
        "configurations_by_structure_family": per_family_group,
        "cost_scenarios_evaluated_per_configuration": space["cost_model"]["friction_stress_pct"],
    }


def emit_shard(rows: list[dict[str, str]], space: dict[str, Any], offset: int, limit: int, output: Path) -> dict[str, Any]:
    if offset < 0 or limit < 1:
        raise ValueError("offset must be >= 0 and limit must be >= 1")
    total = sum(candidate_size(r, space) for r in rows)
    if offset > total:
        raise ValueError(f"offset {offset} exceeds total configuration count {total}")
    stop = min(offset + limit, total)
    cursor = 0
    emitted = 0
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as fh:
        for row in rows:
            if emitted >= stop - offset:
                break
            for dims in branches_for(row, space):
                n = product_size(dims)
                lo = max(0, offset - cursor)
                hi = min(n, stop - cursor)
                if hi > lo:
                    for j in range(lo, hi):
                        config = unrank_product(dims, j)
                        config["configuration_id"] = config_id(space["grid_version"], row["candidate_id"], config)
                        record = {
                            "grid_version": space["grid_version"],
                            "candidate_id": row["candidate_id"],
                            "family_id": row["family_id"],
                            "selector_mode": row["selector_mode"],
                            "configuration": config,
                            "evaluation_scenarios": space["cost_model"]["friction_stress_pct"],
                            "status": "QUEUED_NOT_BACKTESTED",
                        }
                        fh.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
                        emitted += 1
                cursor += n
                if emitted >= stop - offset:
                    break
            if emitted >= stop - offset:
                break
    return {
        "grid_version": space["grid_version"],
        "start_offset": offset,
        "next_offset": stop,
        "configurations_emitted": emitted,
        "total_configurations": total,
        "enumeration_complete": stop >= total,
        "status": "QUEUED_NOT_BACKTESTED",
        "output": str(output),
    }


def self_test() -> None:
    dims = [("a", [1, 2]), ("b", ["x", "y", "z"]), ("c", [False, True])]
    expected = list(itertools.product([1, 2], ["x", "y", "z"], [False, True]))
    got = [tuple(unrank_product(dims, i)[k] for k, _ in dims) for i in range(product_size(dims))]
    assert got == expected, "mixed-radix unranking does not match itertools.product"
    assert len({config_id("g1", "c1", dict(zip(("a","b","c"), row))) for row in expected}) == len(expected)
    print("SELF_TEST_PASS: deterministic Cartesian unranking and IDs")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--audit-out", type=Path)
    parser.add_argument("--emit-shard", type=Path)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=10000)
    args = parser.parse_args()
    if args.self_test:
        self_test()
    rows, space = read_inputs()
    errors = validate(rows, space)
    if errors:
        print(json.dumps({"status": "REGISTRY_INVALID", "errors": errors}, indent=2), file=sys.stderr)
        return 2
    report = audit(rows, space)
    report["registry_validation"] = "PASS"
    report["warnings"] = [
        "Configuration enumeration is not a backtest.",
        "No candidate may be scientifically promoted before source-complete replay, matched controls, costs and OOS gates pass.",
        "Some multi-leg families require an explicit payoff-leg specification before numerical replay."
    ]
    if args.audit_out:
        args.audit_out.parent.mkdir(parents=True, exist_ok=True)
        args.audit_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if args.emit_shard:
        shard = emit_shard(rows, space, args.offset, args.limit, args.emit_shard)
        print(json.dumps(shard, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
