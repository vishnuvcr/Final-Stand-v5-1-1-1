# Phase 33 Data Dictionary

## Time anchor
Reference event = exact 10:00 IST on E minus 6 calendar days.
Target = NIFTY close on expiry E, using the latest complete spot observation at or before 15:29 IST.

## Price and volatility
Daily NIFTY returns, rolling volatility, intraday 10:00 return, ranges, drawdowns, RSI, MACD, moving-average gap and return/volatility ratios.

## Cross-market
Previous available session returns/levels for S&P 500, Nasdaq, Dow, VIX, Nikkei, Sensex, USDINR, gold and crude. Same-day observations are not used when their local market may still be open at the Indian 10:00 cutoff.

## Options
At the reference timestamp, nearest-ATM current-week NIFTY call/put premium, OI, volume, OI-PCR, volume-PCR and normalized ATM straddle from the available option-chain file. Missing contract observations remain missing.

## Sentiment
Daily aggregate sentiment from the point-in-time Indic-Finance HF dataset. The dataset starts in January 2024, so the sentiment-augmented SOFNN track is trained on 2024, validated on 2025 and held out on 2026. Dataset forward-return/target fields are excluded.

## FII/DII
Daily institutional net-flow and index-position fields from the cached MrChartist FII/DII history snapshot, used only from the previous available publication date. Official NSE reports are the authoritative reference for the concept; the open-source cache is used for reproducible historical ingestion. Where the cache has no date, the feature remains missing.

## Leakage controls
All joins are backward-looking. A feature may only use information observable before the 10:00 reference timestamp. No future target column is used as a predictor.

## Data limitations
Public option-chain coverage is incomplete. Sentiment and open-source FII/DII history have narrower historical coverage than NIFTY spot. Missingness is reported rather than imputed from future observations.
