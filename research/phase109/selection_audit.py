"""Multiple-testing controls for Phase 109.

Implements Holm step-down family-wise error control over preregistered,
uniquely keyed hypotheses. Input p-values must be valid unadjusted p-values
from the declared untouched test and must not be selected using the same test.
"""
import math
from typing import Hashable, Iterable


def holm(tests: Iterable[tuple[Hashable, float]], alpha: float = 0.05):
    """Return (adjusted_p_by_identity, rejected_by_identity, number_of_tests).

    Adjusted p-values are monotone in sorted p-value order and capped at 1.
    Identity keys must be unique to avoid silently overwriting a test.
    """
    tests=list(tests)
    if not 0 < alpha < 1:
        raise ValueError("alpha must be strictly between 0 and 1")
    seen=set()
    normalized=[]
    for identity,p in tests:
        try:
            hash(identity)
        except TypeError as exc:
            raise TypeError("test identity must be hashable") from exc
        if identity in seen:
            raise ValueError(f"duplicate test identity: {identity!r}")
        seen.add(identity)
        p=float(p)
        if not math.isfinite(p) or not 0 <= p <= 1:
            raise ValueError(f"invalid p-value for {identity!r}: {p!r}")
        normalized.append((identity,p))
    n=len(normalized)
    ordered=sorted(normalized,key=lambda item:(item[1],repr(item[0])))
    adjusted={}
    running=0.0
    for rank,(identity,p) in enumerate(ordered):
        value=min(1.0,(n-rank)*p)
        running=max(running,value)
        adjusted[identity]=running
    rejected={identity:(adjusted[identity] <= alpha) for identity,_ in normalized}
    return adjusted,rejected,n
