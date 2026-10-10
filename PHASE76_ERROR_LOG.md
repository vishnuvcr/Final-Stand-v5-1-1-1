# Phase 76 Error / Blocker Log
Date: 2026-10-10

## B76-001 — Target files may be absent or stale
- Status: OPEN pending workflow.
- Inspect repository metadata and file contents; never assume filenames imply target-date data.
- If either exact expiry file is absent, stop after the bounded metadata check and record NO-GO.

## B76-002 — License and raw-data retention
- Status: OPEN.
- Dataset card lists CC-BY-NC-4.0. Do not redistribute raw files or commit raw prices; keep downloads in ephemeral workflow storage and persist only aggregate diagnostics.

## B76-003 — Contract mapping and execution quality
- Status: OPEN.
- Explicit expiry/strike/option side fields are necessary but not sufficient: each frozen leg and timestamp window must be verified. OHLC is not bid/ask/depth; any replay must include Paytm Money costs and conservative slippage/spread.
