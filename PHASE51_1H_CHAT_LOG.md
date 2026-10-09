# Phase 51-1H Action Log

## 2026-10-09 — Final public-byte re-audit

A new branch was created because the live Hugging Face repository visibly contained files for both missing expiries. The files were downloaded in GitHub Actions using HF_TOKEN and audited before any P&L.

First implementation failure: the validator assumed the historical RISSIN schema and attempted to read datetime before recording the actual source columns. This was corrected and logged.

Second correction: the current source schema was found to be timestamp/expiry/strike/option_type. A transparent canonical mapping was added without altering raw values.

Final accepted source findings:
- 2026-07-28: 320,359 rows, SHA-256 f9c3a6d1e4498274644ccbfeb8aeb3d545fc2ce1a12b908f450360a643e40d17, actual data ends 2026-07-02.
- 2026-08-04: 2,646 rows, SHA-256 8de2f08cef1456c448c4fc4be0d9d586a1b26af30bf67990171385361af92f9c, actual data ends 2026-07-02.

Both are rejected for the frozen OOS gap.

StockMock and StockMojo were also checked. They remain useful external oracle/context sources but are not accepted as raw repository evidence.

Phase 51 remains DATA-BLOCKED.

## 2026-10-09 — Dataset freshness recheck requested

A fresh public Hugging Face search now surfaces the NIFTY expiry file `options/NIFTY/2026-08-04.parquet` under a newer visible repository commit (51ca58c). The prior accepted byte audit found that the then-current file did not contain the target trading session. File presence/expiry naming alone does not prove complete target-date coverage, so no old result is overwritten or accepted. Trigger marker advanced to `rerun-4 public dataset freshness audit 2026-10-09` to re-download both missing files and re-check raw timestamps, expiry values, duplicate keys and hashes. New result is pending; no P&L is authorized.
