# Error Log

| Date | Phase | Error / limitation | Action |
|---|---|---|---|
| 2026-10-02 | Phase 0 | Repository was initially empty. | Initialized research structure. |
| 2026-10-02 | Phase 1 | Hidden chain-of-thought cannot be exported into the repository. | Record concise reproducible decisions and research updates instead. |
| 2026-10-02 | Phase 1 | Earlier artifacts introduced a stop-loss phase not requested. | Removed stop-loss from the primary strategy. |
| 2026-10-02 | Phase 1 | Earlier implementation evaluated only OTM6/7/8. | Replaced with all n=6..15 candidates and global maximum selection. |
| 2026-10-02 | Phase 1 | n=15 requires OTM17. | Added explicit OTM17 validation. |
| 2026-10-02 | Phase 2 | Primary dataset notes sparse/absent far strikes. | Missing candidate/expiry observations are logged instead of imputed. |
| 2026-10-02 | Phase 2 | Workflow dispatch/readback and direct internet execution are unavailable in this session. | Committed the runnable workflow; no unverified performance result is reported. |
| 2026-10-02 | Phase 2 | Lot-size transition was initially mapped from Nov-2024 instead of expiry-specific transition. | Corrected to 25 through 19-Dec-2024 weekly expiry and 75 from 02-Jan-2025 weekly expiry using NSE circulars. |
| 2026-10-02 | Phase 2 | Push-triggered workflow could retrigger itself after persisting results. | Changed Phase 2 workflow to manual workflow_dispatch only. |
| 2026-10-02 | Phase 2 | Prior workflow could pass an empty HF_TOKEN. | Current workflow uses anonymous public access unless a real token is supplied outside the workflow. |

| 2026-10-02 | Phase 2 | Original execution window covered only 2024–2025 despite the dataset advertising approximately 2021–2026. | Expanded workflow/script defaults to 2021-01-01 through 2026-09-30. |
| 2026-10-02 | Phase 2 | Expanded period required additional historical NIFTY lot-size transitions. | Updated date-aware lot mapping; primary backtest still logs data gaps rather than imputing. |
| 2026-10-02 | Phase 2 | A 2017–2020 public minute dataset was found, but it uses a different file organization/schema. | Recorded it as a supplemental source; require schema/coverage validation before merging. |

| 2026-10-02 | Phase 2 | Verification found stale 2024–2025 fallback values in the workflow/script after the first expansion edit. | Rechecked both files and corrected all default/fallback dates to 2021-01-01 through 2026-09-30; bumped cache key to v3. |

| 2026-10-02 | Phase 2 | Audit found that the first documentation-file writes were absent from the current branch tree. | Restored DATA_ACQUISITION.md and ZENODO_2019_2020_VALIDATION.md and verified the tree. |
| 2026-10-02 | Phase 2 | Backtest used the full expiry-file strike list to define ATM/OTM ranks, creating potential strike-list look-ahead. | Changed ATM/OTM strike discovery to the 10:00 entry snapshot only. |
| 2026-10-02 | Phase 2 | Expiry list did not explicitly exclude monthly expiries from the weekly-options sample. | Excluded the final available expiry date in each calendar month. |
| 2026-10-02 | Phase 2 | NIFTY 65-lot transition was initially applied from Jan-2026 rather than the first revised weekly expiry. | Corrected boundary to 06-Jan-2026 using NSE FAOP70616. |
