# Phase 76 Error / Blocker Log
Date: 2026-10-10

## B76-001 — Target expiry files are present but stale/incomplete
- Status: CLOSED as a source suitability decision; NO-GO for these two dates.
- Corrected workflow run 38042745566 found both files, but both stop at trade date 2026-07-02. Neither contains observations on expiry 2026-07-28 or 2026-08-04.
- 2026-07-28 file: 320,359 rows over 13 trade days; last trade day 2026-07-02; zero expiry-session rows.
- 2026-08-04 file: 2,646 rows over 6 trade days; last trade day 2026-07-02; zero expiry-session rows.
- Decision: do not use these files to fill the missing expiries. Exclude both dates and continue with the validated remaining sample.

## B76-002 — Initial audit date-filter bug
- Status: CLOSED; corrected and rerun.
- Initial run 38042628709 mistakenly required trade timestamp date to equal expiry date, which reported zero rows without checking the rest of the expiry file. The corrected audit groups by explicit expiry and actual trade date, and checks whether the expiry session is present.
- Corrected run: 38042745566. It confirms the source files are incomplete for the target expiry sessions, independently of the initial filter bug.

## B76-003 — License and raw-data retention
- Status: MONITORING.
- Dataset card lists CC-BY-NC-4.0. No raw files or prices were committed; downloads were kept in ephemeral workflow storage and only aggregate diagnostics were published.

## B76-004 — Contract mapping and execution quality
- Status: OPEN downstream limitation.
- Exact expiry/strike/side schema is available in the source, but missing expiry-session data blocks replay. OHLC is not bid/ask/depth; any replay on the remaining sample must include Paytm Money costs and conservative slippage/spread.
