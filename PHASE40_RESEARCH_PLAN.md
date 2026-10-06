# Phase 40 Research Plan — Exhaustive Ensemble Direction Selection

## Research question
Can combinations of the previously tested NIFTY direction selectors, used in parallel and in VIX-gated series, outperform the canonical stateful direction rule after all transaction costs and slippage?

## Frozen experts
- CATBOOST
- DART
- WAVELET_TREE
- OOF_STACK
- MARKOV_REGIME_TREE
- VIX

The five model experts use the already accepted polarity:
- p >= 0.50 -> NIFTY bullish -> PUT spread
- p < 0.50 -> NIFTY bearish -> CALL spread

India VIX is the preferred volatility input. The repository's cached global_VIX/global_VIX_ret1 is retained as an audit fallback.

## Registered steps
1. Audit frozen expert probabilities, split boundaries, polarity and VIX alignment.
2. Exhaustively test every non-empty subset of the six experts: 63 subsets.
3. For each subset test four fixed aggregators: mean, median, majority, confidence-weighted mean.
4. Test seven pre-registered VIX modes: OFF, VIX expert, high-regime gate, low-regime gate, rising gate, falling gate, high+rising stress gate.
5. Screen the complete grid on 2024–2025 fixed opportunities.
6. Freeze the top 10 candidates using validation-only rules.
7. Replay the top 10 through the exact stateful Phase-32 engine.
8. Evaluate only the frozen top 10 on the untouched 2026 holdout.
9. Run sequential routing experiments: ensemble -> VIX gate -> canonical fallback and VIX regime -> expert subset -> ensemble.
10. Apply paired-expiry bootstrap, sign-flip tests, drawdown, profit factor, win rate and +50/+100% cost stress.
11. Write manuscript, charts, tables, status, README and error log.

## Selection rule
Validation-only selection first maximizes control-relative net P&L uplift, then requires acceptable CALL/PUT asymmetry and positive +50% cost-stress uplift when available. Simpler combinations win near-ties.

## Control
Canonical Phase-32/38 stateful direction rule remains the comparator. Frozen validation control is ₹63,672.5753 on the accepted Phase-39 slice.

## Costs
All exact replays use the repository's one-tick adverse slippage and brokerage, exchange, SEBI, IPFT, STT, stamp duty and GST model.

## Stop condition
After the registered 1,764 grid candidates are screened, top candidates are sequentially replayed, untouched holdout is evaluated, and statistical robustness is documented, the phase closes. No unregistered architecture expansion.
