# Phase 29 Delta-Change Exit Research — Final Conclusion

No target-percentage criterion was used. Candidate target and stop exits were driven entirely by short-leg absolute-delta change. Delta coverage was 99.21%.

Training-selected target: MEAN target, 5-minute lookback, 0.20 delta-change threshold, 3-minute confirmation.

Training-selected stop: S1 stop, 1-minute lookback, 0.05 delta-change threshold, 3-minute confirmation. The selected stop produced zero uplift in all partitions.

Against the no-stop dynamic-n diagnostic control:
- Training: +₹20,215.16
- Validation: +₹831.46
- 2026 holdout: −₹574.69
- Full sample: +₹20,471.92

The canonical Phase-20 comparison is the decision standard:
- Training: +₹18,251.49
- Validation: −₹1,092.14
- 2026 holdout: −₹6,879.84
- Full sample: +₹10,279.51

Therefore the candidate fails the required out-of-sample promotion gate.

**Decision: REJECT. Phase 20 remains canonical.**

The full-sample gain is development-dominated and does not persist in the 2026 holdout. No live deployment recommendation follows.
