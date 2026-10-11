#!/usr/bin/env python3
"""Reconcile option archive availability against the official NSE Indices calendar.

The index date series is an observed-session proxy, not a legal exchange calendar
by itself. Missing index dates and range boundaries remain explicitly reported.
"""
import csv, json
from datetime import datetime, timezone
from pathlib import Path

OUT=Path("results/phase109")

def main():
    option_path=OUT/"nse_index_options_daily_coverage.csv"
    calendar_path=OUT/"niftyindices_session_calendar.csv"
    if not option_path.exists() or not calendar_path.exists():
        raise FileNotFoundError("Run NSE option backfill and NSE Indices context audit first.")
    options={r["expected_date"]:r for r in csv.DictReader(option_path.open(encoding="utf-8"))}
    calendar={r["date"]:r for r in csv.DictReader(calendar_path.open(encoding="utf-8"))}
    sessions={d for d,r in calendar.items() if r.get("nifty50_present")=="1"}
    vix_sessions={d for d,r in calendar.items() if r.get("india_vix_present")=="1"}
    bank_sessions={d for d,r in calendar.items() if r.get("nifty_bank_present")=="1"}
    valid_archives={d for d,r in options.items() if r.get("status") in {"DOWNLOADED_AND_PARSED","CACHE_HIT_VALIDATED"}}
    archive_on_session=valid_archives & sessions
    sessions_missing=sorted(sessions-valid_archives)
    archives_no_index=sorted(valid_archives-sessions)
    noarchive={d for d,r in options.items() if r.get("status")=="NO_ARCHIVE_OR_FETCH_ERROR"}
    noarchive_with_index=sorted(noarchive & sessions)
    noarchive_without_index=sorted(noarchive-sessions)
    result={
      "generated_utc":datetime.now(timezone.utc).isoformat(),
      "comparison_range":{"options_min":min(options) if options else "","options_max":max(options) if options else "",
                          "calendar_min":min(calendar) if calendar else "","calendar_max":max(calendar) if calendar else ""},
      "option_weekdays_requested":len(options),
      "official_nifty50_dates_observed":len(sessions),
      "official_india_vix_dates_observed":len(vix_sessions),
      "official_nifty_bank_dates_observed":len(bank_sessions),
      "option_archive_dates_valid":len(valid_archives),
      "valid_archive_dates_also_nifty50_session":len(archive_on_session),
      "observed_nifty50_sessions_without_valid_option_archive":len(sessions_missing),
      "valid_option_archive_dates_without_nifty50_index_date":len(archives_no_index),
      "no_archive_status_on_observed_nifty50_session":len(noarchive_with_index),
      "no_archive_status_on_date_without_nifty50_row":len(noarchive_without_index),
      "sample_missing_archive_dates":sessions_missing[:60],
      "sample_archive_without_nifty50_dates":archives_no_index[:60],
      "sample_no_archive_on_observed_session":noarchive_with_index[:60],
      "sample_no_archive_without_index_row":noarchive_without_index[:60],
      "interpretation":"NIFTY 50 is an observed-session proxy. A date with an official NIFTY 50 observation but no valid option archive is a confirmed coverage gap. A weekday with neither is not automatically a holiday; consult official calendars/exceptions.",
      "raw_price_data_published":False,
    }
    (OUT/"nse_calendar_reconciliation.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    lines=[
      "# NSE archive and NIFTY 50 session-calendar reconciliation","",
      "Generated: "+result["generated_utc"],"",
      "| Metric | Count |","|---|---:|",
      f"| Weekdays requested for option archives | {len(options):,} |",
      f"| Official NIFTY 50 observations | {len(sessions):,} |",
      f"| Official India VIX observations | {len(vix_sessions):,} |",
      f"| Official NIFTY BANK observations | {len(bank_sessions):,} |",
      f"| Valid NSE option archive dates | {len(valid_archives):,} |",
      f"| Option archive dates on NIFTY 50 dates | {len(archive_on_session):,} |",
      f"| NIFTY 50 sessions without a valid option archive | {len(sessions_missing):,} |",
      f"| No-archive statuses on observed NIFTY 50 sessions | {len(noarchive_with_index):,} |",
      f"| Valid option archive dates without NIFTY 50 observations | {len(archives_no_index):,} |",
      f"| Weekday no-archive statuses without index rows (holiday/other uncertain) | {len(noarchive_without_index):,} |","",
      "## Interpretation","",
      "The official NIFTY 50 series is a cross-source proxy for whether the broad Indian cash market traded on a date. A date with a NIFTY 50 observation and no valid option archive is a data coverage gap; do not silently drop it. A weekday with neither source is ambiguous until reconciled against official exchange holidays and exceptions. API earliest/latest dates and unavailable chunks must also be considered.",
      "This does not prove option liquidity or exact contract availability. Each date still needs option-contract identity, lot-size, positive-volume, valid-OHLC and source-quality checks. This is not a performance report.","",
      "See nse_calendar_reconciliation.json for date samples and machine-readable counts."
    ]
    (OUT/"NSE_CALENDAR_RECONCILIATION.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in (
      "option_weekdays_requested","official_nifty50_dates_observed","official_india_vix_dates_observed",
      "official_nifty_bank_dates_observed","option_archive_dates_valid",
      "observed_nifty50_sessions_without_valid_option_archive",
      "no_archive_status_on_observed_nifty50_session","valid_option_archive_dates_without_nifty50_index_date")},sort_keys=True))

if __name__=="__main__": main()
