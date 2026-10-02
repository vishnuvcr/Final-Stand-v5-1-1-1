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
