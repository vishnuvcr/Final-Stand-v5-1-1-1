# Supplemental 2019–2020 Validation

This workflow is a **manual acquisition/validation path** for the Zenodo dataset:

**Nifty spot, futures and options one-minute data from 2017 to 2020**  
DOI: 10.5281/zenodo.10899828

The dataset is 311.9 MB for NIFTY options and describes one-minute fields:
- option type
- strike
- trade date
- trade time
- open/high/low/close
- volume

The dataset documentation states that monthly folders end at the expiry date and contain separate strike files. citeturn0search0

### Why only 2019–2020 can enter this strategy

NIFTY 50 weekly options began trading in February 2019. Therefore the 2017–2018 portion of this dataset cannot be used for the exact weekly-options strategy and is excluded. citeturn5search12

### Validation requirements

Before merging into the primary backtest, the workflow must establish:
1. actual file/schema format;
2. timestamp timezone and 1-minute alignment;
3. CE/PE identification;
4. strike identification;
5. expiry association;
6. presence of the 10:00 entry observation;
7. availability of OTM17 at entry;
8. absence of look-ahead in strike availability;
9. weekly-vs-monthly contract separation;
10. completeness of all three selected legs through exit.

No synthetic values or forward-filled option prices may be introduced.

The Zenodo archive is downloaded into the GitHub Actions cache/workspace rather than committed to Git.
