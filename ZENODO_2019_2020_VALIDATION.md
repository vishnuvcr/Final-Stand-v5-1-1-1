# Supplemental 2019–2020 Zenodo Validation

Source: Zenodo DOI 10.5281/zenodo.10899828.

The archive contains NIFTY one-minute spot/futures/options data for 2017–2020. The documented option fields are option type, strike, trade date, trade time, OHLC and volume.

NIFTY weekly options began in February 2019. Consequently, only the 2019–2020 portion is eligible for the exact weekly-options strategy; 2017–2018 is excluded.

Validation must establish:
1. file and column schema;
2. timezone and minute timestamp convention;
3. CE/PE identification;
4. strike and expiry mapping;
5. weekly versus monthly contract separation;
6. 10:00 entry availability;
7. OTM17 availability at entry;
8. complete three-leg exit series;
9. absence of look-ahead.

A manual workflow downloads the 311.9 MB options archive into an Actions cache, extracts it temporarily, and writes a structural validation manifest. The source is not merged into the primary results until full compatibility validation succeeds.

## Compatibility verdict

**Rejected for primary weekly-contract backtest.** Deep inspection reached the strike-file level. Rows contain symbol, trade date, trade time, OHLC and volume, but no expiry identifier. Strike files span multiple expiry cycles within the monthly archive. Assigning a weekly expiry to each row would require inference not supported by the recorded fields, so the source is not merged into the strategy results.
