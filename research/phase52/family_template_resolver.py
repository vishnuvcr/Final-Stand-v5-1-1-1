#!/usr/bin/env python3
"""Parse registered Phase52 option-leg templates into a fail-closed AST.

No P&L is computed here. The parser consumes the registered family specification
rather than inferring geometry from names/screenshots. Unresolved family
specifications, intraday-futures-dependent families, and synthetic-futures
variants without an approved carry model are blocked before data access.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "research" / "phase52" / "strategy_specifications.csv"
OUT_DIR = ROOT / "results" / "phase52" / "template_resolver"
BLOCKED_SPEC_STATUSES = {"SPECIFICATION_BLOCKED", "PHASE45_TEMPLATE_REQUIRES_RECONCILIATION"}
FUTURES_REQUIRED_FAMILIES = {
    "FUTURES_BASIS_SPREAD", "PROTECTIVE_PUT_FUTURE",
    "COVERED_CALL_FUTURE", "DELTA_NEUTRAL_LONG_GAMMA_SCALP",
}
CARRY_REQUIRED_FAMILIES = {"LONG_SYNTHETIC_FUTURE", "SHORT_SYNTHETIC_FUTURE"}
DIAGNOSTIC_PREFIXES = ("DIAGNOSTIC_ONLY",)

# Each header begins an option leg in the registered template. The tail until the
# next leg/header separator supplies its optional strike expression.
LEG_HEADER = re.compile(
    r"(?P<side>BUY|SELL)\s+(?P<quantity>\d+|R)\s+"
    r"(?:(?P<expiry>near-expiry|later-expiry)\s+)?"
    r"(?:(?P<atm>ATM)\s+)?(?P<option_type>CE|PE)\b",
    re.IGNORECASE,
)
STRIKE_EXPR = re.compile(r"\bK(?:\s*[+-]\s*(?:W\d?|O|\d+))*\b", re.IGNORECASE)
STRIKE_TOKEN = re.compile(r"([+-])\s*(W\d?|O|\d+)", re.IGNORECASE)


@dataclass(frozen=True)
class LegTemplate:
    leg_index: int
    side: str
    quantity_token: str
    quantity: int | None
    option_type: str
    strike_expression: str
    expiry_role: str
    source_fragment: str


@dataclass(frozen=True)
class FamilyResolution:
    family_id: str
    family_name: str
    specification_status: str
    status: str
    reason: str
    legs: tuple[LegTemplate, ...]


def parse_option_legs(template: str) -> tuple[LegTemplate, ...]:
    """Parse one or more option legs; malformed/unparseable text fails closed."""
    text = str(template)
    matches = list(LEG_HEADER.finditer(text))
    legs: list[LegTemplate] = []
    for i, match in enumerate(matches):
        tail_start = match.end()
        tail_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        fragment = text[tail_start:tail_end]
        # The first strike expression ends before a leg separator / later prose.
        expr_match = STRIKE_EXPR.search(fragment)
        expr = expr_match.group(0) if expr_match else "K"
        expr = re.sub(r"\s+", "", expr.upper())
        quantity_token = match.group("quantity").upper()
        quantity = int(quantity_token) if quantity_token.isdigit() else None
        expiry_role = (match.group("expiry") or "selected-expiry").lower()
        legs.append(LegTemplate(
            leg_index=len(legs),
            side=match.group("side").upper(),
            quantity_token=quantity_token,
            quantity=quantity,
            option_type=match.group("option_type").upper(),
            strike_expression=expr,
            expiry_role=expiry_role,
            source_fragment=(match.group(0) + fragment).strip()[:240],
        ))
    return tuple(legs)


def evaluate_strike_expression(
    expression: str,
    anchor_strike: float,
    modal_step: float,
    params: Mapping[str, float],
    numeric_offset_scale: float = 1.0,
) -> float:
    """Evaluate a restricted K±token expression; no eval/exec or substitution."""
    expr = re.sub(r"\s+", "", str(expression).upper())
    if not expr.startswith("K"):
        raise ValueError(f"expression must start with K: {expression!r}")
    if modal_step <= 0:
        raise ValueError("modal_step must be positive")
    total = float(anchor_strike)
    rest = expr[1:]
    pieces = list(STRIKE_TOKEN.finditer(rest))
    if not rest and not pieces:
        return total
    rebuilt = "".join(m.group(0) for m in pieces)
    if rebuilt != rest:
        raise ValueError(f"unsupported strike expression: {expression!r}")
    for match in pieces:
        sign = 1.0 if match.group(1) == "+" else -1.0
        token = match.group(2).upper()
        if token.startswith("W"):
            key = token
            if key not in params:
                raise ValueError(f"missing registered width parameter {key}")
            amount = float(params[key])
        elif token == "O":
            if "O" not in params:
                raise ValueError("missing O offset parameter")
            amount = float(params["O"])
        else:
            amount = float(token) * float(numeric_offset_scale)
        if not amount.is_integer() if isinstance(amount, float) else False:
            pass
        total += sign * amount * float(modal_step)
    return float(round(total, 8))


def resolve_family(row: Mapping[str, Any]) -> FamilyResolution:
    family_id = str(row["family_id"]).strip()
    family_name = str(row["family_name"]).strip()
    specification_status = str(row["specification_status"]).strip()
    template = str(row["leg_template"]).strip()
    if specification_status in BLOCKED_SPEC_STATUSES:
        return FamilyResolution(
            family_id, family_name, specification_status,
            "BLOCKED_SPECIFICATION", "registered template has not been source-reconciled", ()
        )
    if family_id in FUTURES_REQUIRED_FAMILIES:
        return FamilyResolution(
            family_id, family_name, specification_status,
            "BLOCKED_INTRADAY_FUTURES", "synchronized intraday traded-futures bars/costs are unavailable", ()
        )
    if family_id in CARRY_REQUIRED_FAMILIES:
        return FamilyResolution(
            family_id, family_name, specification_status,
            "BLOCKED_CARRY_MODEL", "synthetic-futures financing/carry model is not yet registered", ()
        )
    if family_id == "DELTA_NEUTRAL_LONG_GAMMA_SCALP":
        return FamilyResolution(
            family_id, family_name, specification_status,
            "BLOCKED_INTRADAY_FUTURES", "delta hedge requires synchronized intraday hedge prices", ()
        )
    legs = parse_option_legs(template)
    if not legs:
        return FamilyResolution(
            family_id, family_name, specification_status,
            "BLOCKED_TEMPLATE_PARSE", "no explicit option-leg expression was parsed; do not infer from family name", ()
        )
    if specification_status.startswith(DIAGNOSTIC_PREFIXES):
        status = "DIAGNOSTIC_ONLY"
        reason = "leg map parsed, but registered risk tag forbids promotion"
    else:
        status = "PARSED_SPEC_NOT_DATA_ELIGIBLE"
        reason = "leg map parsed; exact timestamps, selected contracts, OI, risk and exit gates remain"
    return FamilyResolution(family_id, family_name, specification_status, status, reason, legs)


def resolve_spec_file(path: Path = SPEC_PATH) -> tuple[pd.DataFrame, dict[str, Any]]:
    specs = pd.read_csv(path, dtype=str).fillna("")
    required = {"family_id", "family_name", "leg_template", "specification_status", "source_ref", "risk_notes"}
    missing = required - set(specs.columns)
    if missing:
        raise ValueError(f"strategy specification file missing columns {sorted(missing)}")
    if specs["family_id"].duplicated().any():
        duplicates = specs.loc[specs["family_id"].duplicated(), "family_id"].tolist()
        raise ValueError(f"duplicate family IDs: {duplicates}")
    resolved = [resolve_family(row) for row in specs.to_dict("records")]
    output = pd.DataFrame([
        {
            "family_id": r.family_id,
            "family_name": r.family_name,
            "specification_status": r.specification_status,
            "resolution_status": r.status,
            "resolution_reason": r.reason,
            "leg_count": len(r.legs),
            "parsed_legs_json": json.dumps([asdict(x) for x in r.legs], separators=(",", ":")),
            "source_ref": specs.loc[specs["family_id"].eq(r.family_id), "source_ref"].iloc[0],
        }
        for r in resolved
    ])
    counts = output["resolution_status"].value_counts().to_dict()
    summary = {
        "status": "TEMPLATE_RESOLUTION_AUDIT_COMPLETE",
        "families_in_specs": int(len(specs)),
        "families_with_parsed_option_legs": int(output["leg_count"].gt(0).sum()),
        "resolution_status_counts": {str(k): int(v) for k, v in counts.items()},
        "blocked_specification_families": output.loc[output.resolution_status.eq("BLOCKED_SPECIFICATION"), "family_id"].tolist(),
        "blocked_intraday_futures_families": output.loc[output.resolution_status.eq("BLOCKED_INTRADAY_FUTURES"), "family_id"].tolist(),
        "blocked_carry_families": output.loc[output.resolution_status.eq("BLOCKED_CARRY_MODEL"), "family_id"].tolist(),
        "diagnostic_only_families": output.loc[output.resolution_status.eq("DIAGNOSTIC_ONLY"), "family_id"].tolist(),
        "pnl_status": "NO_PNL_COMPUTED",
        "interpretation": "This resolves registered option-leg strings into a structured AST only. It does not choose strikes/expiries, check data or calculate P&L.",
    }
    return output, summary


def self_test() -> None:
    spec = {
        "family_id": "SHORT_IRON_CONDOR",
        "family_name": "Short Iron Condor",
        "specification_status": "STANDARD_VARIANT_PREREGISTERED",
        "leg_template": "BUY 1 PE K-W2; SELL 1 PE K-W1; SELL 1 CE K+W1; BUY 1 CE K+W2; W2>W1",
        "source_ref": "synthetic fixture",
        "risk_notes": "",
    }
    resolved = resolve_family(spec)
    assert resolved.status == "PARSED_SPEC_NOT_DATA_ELIGIBLE"
    assert [(x.side,x.quantity,x.option_type,x.strike_expression) for x in resolved.legs] == [
        ("BUY",1,"PE","K-W2"), ("SELL",1,"PE","K-W1"),
        ("SELL",1,"CE","K+W1"), ("BUY",1,"CE","K+W2")
    ]
    assert evaluate_strike_expression("K-W2", 22000, 50, {"W2":3}) == 21850
    assert evaluate_strike_expression("K+W1+W2", 22000, 50, {"W1":1,"W2":3}) == 22200
    assert evaluate_strike_expression("K+O", 22000, 50, {"O":2}) == 22100
    blocked = resolve_family({**spec,"family_id":"CALENDAR_TRAP","specification_status":"SPECIFICATION_BLOCKED"})
    assert blocked.status == "BLOCKED_SPECIFICATION" and not blocked.legs
    futures = resolve_family({**spec,"family_id":"FUTURES_BASIS_SPREAD"})
    assert futures.status == "BLOCKED_SPECIFICATION"
    carry = resolve_family({**spec,"family_id":"LONG_SYNTHETIC_FUTURE",
                            "leg_template":"BUY 1 CE K; SELL 1 PE K"})
    assert carry.status == "BLOCKED_CARRY_MODEL"
    diag = resolve_family({**spec,"family_id":"SELL_CALL",
                           "specification_status":"DIAGNOSTIC_ONLY_UNDEFINED_RISK",
                           "leg_template":"SELL 1 CE at selected strike/expiry"})
    assert diag.status == "DIAGNOSTIC_ONLY" and len(diag.legs) == 1
    print("SELF_TEST_PASS: multi-leg parse, restricted strike expressions, explicit specification/futures/carry/risk blocks")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test-only", action="store_true")
    args = parser.parse_args()
    if args.self_test_only:
        self_test()
        return 0
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame, summary = resolve_spec_file()
    frame.to_csv(OUT_DIR / "family_templates.csv", index=False)
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
