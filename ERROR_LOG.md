# Error Log

| Date | Phase | Error / limitation | Action |
|---|---|---|---|
| 2026-10-02 | Phase 0 | Repository was initially empty. | Initialized research structure. |
| 2026-10-02 | Phase 1 | Hidden chain-of-thought cannot be exported into the repository. | Record concise reproducible decisions and research updates instead. |
| 2026-10-02 | Phase 1 | Earlier artifacts introduced a stop-loss phase not requested. | Removed stop-loss from the primary strategy. |
| 2026-10-02 | Phase 1 | Earlier implementation evaluated only OTM6/7/8. | Replaced with all n=6..15 candidates and global maximum selection. |
| 2026-10-02 | Phase 1 | n=15 requires OTM17. | Added explicit OTM17 validation. |
| 2026-10-02 | Phase 2 | Primary dataset notes sparse/absent far strikes. | Missing candidate/expiry observations are logged instead of imputed. |
| 2026-10-02 | Phase 2 | Prior workflow could pass an empty HF_TOKEN. | Current workflow uses anonymous public access unless a real token is supplied outside the workflow. |
