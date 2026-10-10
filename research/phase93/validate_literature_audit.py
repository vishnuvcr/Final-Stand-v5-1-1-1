#!/usr/bin/env python3
"""Validate the bounded Phase 93 uploaded-literature audit without downloading data."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "results/phase93/UPLOADED_LITERATURE_AUDIT.md"
MANUSCRIPT = ROOT / "results/phase92/MANUSCRIPT_DRAFT.md"
SUPPLEMENT = ROOT / "results/phase92/SUPPLEMENTARY_MATERIALS.md"
REPORT = ROOT / "results/phase93/validation_report.json"

EXPECTED_FILES = [
    "1-s2.0-S1877050922020993-main.pdf",
    "50375.pdf",
    "9472-Article Text-11108-2-10-20231228.pdf",
    "CureusJournals_1986620261002-185337-d4go5h.pdf",
    "D0801051829.pdf",
    "IJCSE-V11I10P106.pdf",
    "IJNRD2205074.pdf",
    "IJSDR2309053.pdf",
    "ISMLA+7481.pdf",
    "JIER-+Vol.+5+No.+3+(2025)+-+Dr.+Deepesh.Formated.pdf",
    "Stock Market Prediction of NIFTY 50 Index Applying Machine Learning Techniques.pdf",
    "Stock_Market_Index_Forecasting_of_Nifty.pdf",
    "jrfm-16-00423.pdf",
    "ssrn-3323746.pdf",
]

EXPECTED_TITLES = [
    "Stock Market Prediction with High Accuracy using Machine Learning Techniques",
    "Developing a machine learning-based options trading strategy for the Indian market",
    "An efficient approach to forecasting the NIFTY-50 Indian stock market's daily closing price",
    "Open and Close Price Forecasting of the NIFTY 50 Stock Index Using Machine Learning",
    "Options Trading Strategy: A quantitative study from an investor's POV",
    "Bridging temporal dependencies and sentiment",
    "Options trading strategies for the Indian market",
    "NIFTY-50 stock prediction master",
    "Deep learning approaches for stock price prediction",
    "A study of the impact of moving averages",
    "Stock market prediction of NIFTY 50 index applying machine learning techniques",
    "Stock market index forecasting of Nifty 50",
    "Forecasting of NIFTY 50 index price by using backward elimination",
    "Commodity Channel Index for NSE's Nifty options",
]

def main() -> int:
    errors: list[str] = []
    for p in (AUDIT, MANUSCRIPT, SUPPLEMENT):
        if not p.is_file():
            errors.append(f"Missing required file: {p.relative_to(ROOT)}")

    audit = AUDIT.read_text(encoding="utf-8") if AUDIT.is_file() else ""
    manuscript = MANUSCRIPT.read_text(encoding="utf-8") if MANUSCRIPT.is_file() else ""
    supplement = SUPPLEMENT.read_text(encoding="utf-8") if SUPPLEMENT.is_file() else ""

    ids = re.findall(r"^### (U\d{2}) —", audit, flags=re.MULTILINE)
    expected_ids = [f"U{i:02d}" for i in range(1, 15)]
    if ids != expected_ids:
        errors.append(f"Expected ordered U01-U14 sections exactly once; found {ids}")

    for filename in EXPECTED_FILES:
        if filename not in audit:
            errors.append(f"Uploaded filename missing from audit: {filename}")

    for term in ("Paper-reported findings", "Use in this project", "Limitations / interpretation", "Classification"):
        # Each paper section should repeat the key evidence fields.
        if audit.count("**" + term + ":**") < 14:
            errors.append(f"Audit is missing per-source fields for: {term}")

    refs_heading = manuscript.rfind("## References")
    refs_text = manuscript[refs_heading:] if refs_heading >= 0 else ""
    ref_nums = [int(x) for x in re.findall(r"^(\d+)\. ", refs_text, flags=re.MULTILINE)]
    if ref_nums != list(range(1, 30)):
        errors.append(f"Manuscript references should be numbered 1-29; found {ref_nums}")

    for title in EXPECTED_TITLES:
        if title.lower() not in manuscript.lower():
            errors.append(f"Source title missing from manuscript references/review: {title}")

    for required in (
        "### 3.5 Indian NIFTY index-forecasting and technical-feature studies",
        "### 3.6 Indian options-strategy studies",
        "### 3.7 Research gap",
        "not independently reproduced by this project",
        "Paytm Money",
        "Phase 83",
    ):
        if required.lower() not in manuscript.lower():
            errors.append(f"Required manuscript boundary/section missing: {required}")

    if "14 user-uploaded research PDFs" not in supplement:
        errors.append("Supplementary Materials does not point to the 14-paper audit")
    if "does not use the sealed Phase 83 2026 holdout" not in audit:
        errors.append("Audit does not explicitly state that the protected holdout was not used")

    report = {
        "phase": 93,
        "status": "PASS" if not errors else "FAIL",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "audit_sections_found": len(ids),
        "uploaded_file_mappings_expected": len(EXPECTED_FILES),
        "manuscript_reference_numbers_found": ref_nums,
        "manual_model_or_market_data_tests_run": False,
        "phase83_2026_holdout_accessed": False,
        "strategy_promoted": False,
        "errors": errors,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
