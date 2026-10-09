# Phase 53 data source matrix

**Scope:** free-access public metadata/source audit. Free page/code does not imply free full data, redistribution permission, intraday granularity, or suitability for executable fills.

| Source | Access/licence evidence | Fields/granularity expected | Candidate role | Known limitation | Phase decision |
|---|---|---|---|---|---|
| Hugging Face thetrademarkk/india-index-options-1m, pinned revision 0f4800e43e6f96cec0794369d78eb4d3c4211ef5 | Public dataset card declares CC BY-NC 4.0 | One-minute OHLCV + OI; index and option partitions with strike, expiry, CE/PE | Primary exploratory baseline | Option coverage is partial/sparse; no quoted bid/ask or depth fields documented; non-commercial licence | Audit pinned files and exact timestamps; research-only |
| NSE All Reports — F&O UDiFF Bhavcopy, NCL/Combined OI, participant-wise OI/volume, FII derivative statistics | Official exchange report portal | Daily end-of-day contract and aggregate participant reports; individual files vary by report | Daily controls, expiry/lot/settlement reconciliation, PIT participant factors | Not a substitute for 1-minute exact prior-bar OI or option quotes | Include in a separate daily-factor validation arm only |
| NSE EOD historical data subscription | Official NSE market-data page notes EOD historical products | Daily historical outputs, product-specific | Establish paid vs publicly downloadable scope | Some historical products are subscription-based | Do not treat paid data as free |
| BSE derivative historical pages and file-format docs | Official BSE pages; daily contract files may expose close/settlement/OI | Daily contract-level price/volume/OI, historical contract inquiry; current pages vary | Independent daily cross-check, especially BSE/SENSEX products | Availability, granularity and terms need per-endpoint validation; BSE market-data feeds include paid products | Audit only; no assumption that daily files repair intraday rows |
| OptionVault public GitHub repository | Public repository/code and samples; README says full 300+ GB dataset available to licensed users | Repository describes one-minute options OHLC/OI/Greeks/depth fields | Schema documentation and small sample validation | Sample files are explicitly evaluation-only; complete data is licensed | Not an eligible free full-history source unless licence/access changes |
| Breeze historical options pipeline | Public code; requires ICICI Direct account, Breeze API key and fresh session | Claimed 1-minute OHLCV + OI across CE/PE strikes | Conditional authenticated acquisition design | Not unauthenticated public data; no credential provided/used in Phase 53 | Document as credential-dependent; do not call API |
| Paid options-data storefronts | Product listings are public; data requires purchase | May advertise intraday OI or full chains | Potential future procurement option | Paid; not a free-source solution, no purchase authorized | Exclude from current phase |
| Kaggle/Hugging Face/GitHub mirrors discovered later | Source/revision must be recorded before review | Unknown until actual schema/file is checked | Potential independent coverage challenger | May be partial, copied, synthetic, sample-only or differently licensed | Never accept based on a title/README alone |

## Publicly verified facts and references

- NSE's official F&O reports portal lists UDiFF common bhavcopy, NCL open interest, combined open interest, participant-wise open interest/trading volumes, and FII derivatives statistics. These are report products, not blanket proof of intraday quote coverage: https://www.nseindia.com/all-reports-derivatives
- The HF dataset card declares CC BY-NC 4.0, describes one-minute OHLCV(+OI), and explicitly warns that option coverage is partial and illiquid/far strikes may be sparse or absent: https://huggingface.co/datasets/thetrademarkk/india-index-options-1m
- OptionVault's README states public repository samples are for evaluation and complete data are available to licensed users: https://github.com/QuantDev-stack/OptionVault
- The Breeze pipeline README requires an ICICI Direct account, Breeze API key and renewed session token: https://github.com/mukhilj/breeze_options_pipeline
- BSE derivative file format documentation describes end-of-day contract-file and bhavcopy fields, including strike, option type, OHLC, volume and OI: https://www.bseindia.com/downloads1/File_Format_Equity_Derivatives.pdf
- Paytm Money F&O fee assumptions remain inherited from Phase 52 until account-specific tariff is confirmed; retain ₹10/₹20 per-order cases and all statutory and slippage components in any later net-P&L replay.

**Decision:** No external source is considered to have solved the intraday quote-quality gap until exact downloaded files, schema, revision, licence and contract-time coverage pass the Phase 53 gates.
