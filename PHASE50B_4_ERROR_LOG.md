# Phase 50B-4 Error Log

No execution error has occurred in Phase 50B-4 yet.

Pre-execution controls:
- geometry universe is frozen;
- BASE is verified from accepted TT-03 V5 evidence;
- OTM350 and OTM400 are the only mutations;
- development selection is frozen before validation/holdout interpretation;
- coverage and data-error gates remain fail-closed.

## 2026-10-09 — Error F50B4-001

Actions run 37848842347 stopped at BASE verification because pandas was absent from that job environment. No OTM numerical replay ran and no evidence was produced. A pandas install step was added to the verification job.

## 2026-10-09 — Error F50B4-002

Actions run 37848915637: OTM350 numerical replay completed and produced a source-faithful result, but the audit step failed because TT03_DISTANCE was not exported into the audit step environment. This was a workflow/audit packaging defect, not a replay/data failure. The numerical output was therefore rejected from evidence publication and the branch was corrected to export the matrix distance before accepting any result.
