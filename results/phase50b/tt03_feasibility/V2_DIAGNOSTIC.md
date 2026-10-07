# TT-03 V2 Feasibility Diagnostic — NON-EVIDENCE

## V2 result
- Run: 37613416831
- Engine: 50B-TT03-WINDOW-V2
- Complete campaigns: 187
- Candidate campaigns: 202
- Coverage: 92.5743%
- Feasibility threshold: 95%
- Decision: FAIL_COVERAGE; no V2 P&L is admissible evidence.

## Gap classification
The archived V2 diagnostic contained 15 exclusions:

| Class | Count | Interpretation |
|---|---:|---|
| Missing CE leg at 15:29 hard-close timestamp | 13 | The V2 engine selected a latest timestamp containing some option data and then failed if the CE leg was absent. V3/V4 searches backward for the latest timestamp at or before 15:29 where all live legs are simultaneously quoted. |
| No 10:00–10:05 observation on a normal trading day | 1 | 2022-03-07. This remains a genuine data-coverage problem because the date had a normal exchange trading session but the required entry window was unobserved. |
| No normal 09:15–15:30 session on intended entry date | 1 | 2022-10-24. NSE scheduled a Diwali Muhurat session beginning at 18:15, so the source strategy's 10:00–10:05 entry did not have a normal-session opportunity. V4 records this as a session exclusion rather than a coverage failure. |

Official NSE references:
- https://archives.nseindia.com/content/circulars/FAOP54024.pdf
- https://archives.nseindia.com/content/circulars/FAOP50561.pdf

## Consequence
The V2 feasibility failure is retained as a diagnostic control result, not as a strategy rejection. V4 must re-establish the coverage denominator using the corrected hard-close search and session accounting. Only the V4 run can determine whether TT-03 passes the preregistered 95% feasibility gate.
