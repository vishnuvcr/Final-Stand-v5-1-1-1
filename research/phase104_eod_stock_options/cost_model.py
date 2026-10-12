"""Date-effective indicative options fees for Phase 104; execution slippage is separate."""
from datetime import date

GST_RATE = 0.18
STAMP_DUTY_BUY_RATE = 0.00003        # 0.003% of option premium turnover
SEBI_TURNOVER_FEE_RATE = 0.000001    # 0.0001% of premium turnover
STT_SELL_RATE_BEFORE_2026_04_01 = 0.0010
STT_SELL_RATE_FROM_2026_04_01 = 0.0015


def exchange_transaction_rate(trade_date):
    """Return proportion per side for NSE equity-options premium turnover."""
    day = date.fromisoformat(trade_date) if isinstance(trade_date, str) else trade_date
    if day >= date(2026, 3, 1):
        return 0.0003552  # ₹3,552 per crore premium value, effective 2026-03-01
    if day >= date(2024, 10, 1):
        return 0.0003503  # ₹35.03 per ₹1 lakh premium value
    raise ValueError("Exchange-fee schedule before 2024-10-01 is outside this registered model.")


def ipft_contribution_rate(trade_date):
    """Indicative NSE IPFT contribution rate on option premium; exact contract-note treatment may differ."""
    day = date.fromisoformat(trade_date) if isinstance(trade_date, str) else trade_date
    if day >= date(2026, 3, 1):
        return 0.000000001  # ₹0.01 per crore, exact rate (NSE circular's table rounds total outflow)
    if day >= date(2024, 10, 1):
        return 0.000005      # ₹50 per crore, previous contribution in NSE circular
    raise ValueError("IPFT schedule before 2024-10-01 is outside this registered model.")


def round_trip_cost(
    buy_premium,
    sell_premium,
    quantity,
    trade_date,
    brokerage_per_order=20.0,
    exercised_intrinsic_value=0.0,
):
    """Estimate reported statutory/service fees for a long option round trip.

    The result intentionally excludes bid/ask spread, slippage, latency, impact, partial
    fills and any exercise cost beyond the explicitly supplied intrinsic-value amount.
    It is a cost schedule, not an executable P&L estimate.
    """
    day = date.fromisoformat(trade_date) if isinstance(trade_date, str) else trade_date
    if buy_premium < 0 or sell_premium < 0 or quantity <= 0 or brokerage_per_order < 0:
        raise ValueError("Premia and brokerage must be non-negative; quantity must be positive.")
    buy_turnover = float(buy_premium) * int(quantity)
    sell_turnover = float(sell_premium) * int(quantity)
    total_turnover = buy_turnover + sell_turnover
    exchange_rate = exchange_transaction_rate(day)
    exchange_fee = total_turnover * exchange_rate
    ipft_fee = total_turnover * ipft_contribution_rate(day)
    brokerage = 2.0 * float(brokerage_per_order)
    sebi_fee = total_turnover * SEBI_TURNOVER_FEE_RATE
    # GST base includes brokerage, exchange transaction charges and SEBI fees.
    # Treatment of separately billed IPFT contribution must be reconciled to the broker's contract note.
    gst = GST_RATE * (brokerage + exchange_fee + sebi_fee)
    stt_rate = STT_SELL_RATE_FROM_2026_04_01 if day >= date(2026, 4, 1) else STT_SELL_RATE_BEFORE_2026_04_01
    stt = sell_turnover * stt_rate
    if exercised_intrinsic_value < 0:
        raise ValueError("Exercised intrinsic value must be non-negative.")
    exercised_stt = 0.0
    if exercised_intrinsic_value:
        exercise_rate = 0.0015 if day >= date(2026, 4, 1) else 0.00125
        exercised_stt = float(exercised_intrinsic_value) * int(quantity) * exercise_rate
    stamp_duty = buy_turnover * STAMP_DUTY_BUY_RATE
    costs = {
        "brokerage": brokerage,
        "exchange_transaction_charges": exchange_fee,
        "nse_ipft_contribution": ipft_fee,
        "sebi_turnover_fee": sebi_fee,
        "gst_on_service_fees": gst,
        "stt_on_option_sale": stt,
        "stamp_duty_on_option_buy": stamp_duty,
        "stt_on_exercise_if_applicable": exercised_stt,
    }
    costs["total_reported_fees"] = sum(costs.values())
    costs["buy_premium_turnover"] = buy_turnover
    costs["sell_premium_turnover"] = sell_turnover
    costs["exchange_rate_per_side"] = exchange_rate
    costs["ipft_rate"] = ipft_contribution_rate(day)
    costs["stt_sell_rate"] = stt_rate
    costs["brokerage_per_order_assumption"] = float(brokerage_per_order)
    costs["execution_spread_slippage_impact"] = None
    costs["net_pnl_status"] = "NOT_COMPUTABLE_WITHOUT_EXECUTABLE_FILL_MODEL"
    # Keep reported rates at high precision; rounding a rate such as 0.0003552
    # to six decimal places would misreport the official 2026 exchange charge.
    return {
        k: (round(v, 12) if "rate" in k else round(v, 6))
        if isinstance(v, float) else v
        for k, v in costs.items()
    }
