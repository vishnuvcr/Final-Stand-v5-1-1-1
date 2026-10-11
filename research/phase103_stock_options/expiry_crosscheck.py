"""Independent Dhan rolling-option expiry cross-check against NSE daily F&O bhavcopy.
All row-level Dhan and NSE values remain in memory. Only aggregate counts/status are returned.
"""
import csv, io, zipfile
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

NSE_URL = "https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{date}_F_0000.csv.zip"
IST = ZoneInfo("Asia/Kolkata")
EXPECTED_SESSION_MINUTES = 385
PRICE_TOLERANCE = 0.051
NSE_REQUIRED = {"FinInstrmTp", "TckrSymb", "XpryDt", "StrkPric", "OptnTp", "OpnPric", "HghPric", "LwPric", "ClsPric", "TtlTradgVol", "OpnIntrst"}


def _float(value):
    try:
        number = float(str(value).strip())
        if number != number or abs(number) == float("inf"):
            return None
        return number
    except (ValueError, TypeError, OverflowError):
        return None


def _norm_num(value):
    number = _float(value)
    return None if number is None else format(number, ".10g")


def _parse_date(value):
    value = str(value or "").strip()
    for fmt in ("%Y-%m-%d", "%d-%b-%Y", "%d-%B-%Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def parse_nse_bhavcopy(payload):
    """Parse only stock-option EOD fields needed for identity checking."""
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(names) != 1:
            raise ValueError("Expected exactly one CSV in NSE F&O bhavcopy ZIP")
        content = archive.read(names[0]).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames or not NSE_REQUIRED.issubset(set(reader.fieldnames)):
        raise ValueError("NSE UDiFF schema missing required stock-option columns")
    rows = []
    for item in reader:
        instrument = str(item.get("FinInstrmTp", "")).strip().upper()
        if instrument and instrument not in {"STO", "OPTSTK"}:
            continue
        symbol = str(item.get("TckrSymb", "")).strip().upper()
        option_type = str(item.get("OptnTp", "")).strip().upper()
        strike = _norm_num(item.get("StrkPric"))
        expiry = _parse_date(item.get("FininstrmActlXpryDt")) or _parse_date(item.get("XpryDt"))
        if not symbol or option_type not in {"CE", "PE"} or strike is None or expiry is None:
            continue
        rows.append({
            "symbol": symbol, "option_type": option_type, "strike": strike, "expiry": expiry,
            "open": _float(item.get("OpnPric")), "high": _float(item.get("HghPric")),
            "low": _float(item.get("LwPric")), "close": _float(item.get("ClsPric")),
            "volume": _float(item.get("TtlTradgVol")), "oi": _float(item.get("OpnIntrst")),
        })
    return rows


def _extract_profiles(surface_blocks):
    """Create exact (symbol, side, date, strike) daily profiles from ephemeral minute rows."""
    by_key = {}
    duplicate_keys = conflict_keys = 0
    for block in surface_blocks:
        bars = block.get("bars")
        if not isinstance(bars, dict):
            continue
        fields = ("timestamp", "strike", "open", "high", "low", "close", "volume", "oi")
        arrays = {key: bars.get(key, []) for key in fields}
        lengths = [len(v) for v in arrays.values() if isinstance(v, list)]
        if not lengths or len(set(lengths)) != 1:
            continue
        for i in range(lengths[0]):
            try:
                ts = int(arrays["timestamp"][i])
                dt = datetime.fromtimestamp(ts, timezone.utc).astimezone(IST)
            except (ValueError, TypeError, OverflowError, OSError):
                continue
            strike = _norm_num(arrays["strike"][i])
            if strike is None:
                continue
            row = {"timestamp": ts, "open": _float(arrays["open"][i]), "high": _float(arrays["high"][i]),
                   "low": _float(arrays["low"][i]), "close": _float(arrays["close"][i]),
                   "volume": _float(arrays["volume"][i]), "oi": _float(arrays["oi"][i])}
            key = (block["symbol"], block["option_type"], dt.date().isoformat(), strike, ts)
            if key not in by_key:
                by_key[key] = row
            else:
                duplicate_keys += 1
                previous = by_key[key]
                if previous is not None and any(previous[f] != row[f] for f in ("open", "high", "low", "close", "volume", "oi")):
                    conflict_keys += 1
                    by_key[key] = None
    grouped = defaultdict(list)
    for key, row in by_key.items():
        if row is None:
            continue
        symbol, side, day, strike, _ = key
        grouped[(symbol, side, day, strike)].append(row)
    profiles = []
    for (symbol, side, day, strike), rows in grouped.items():
        rows.sort(key=lambda x: x["timestamp"])
        stamps = [r["timestamp"] for r in rows]
        times_ist = [datetime.fromtimestamp(ts, timezone.utc).astimezone(IST) for ts in stamps]
        full = (len(set(stamps)) == EXPECTED_SESSION_MINUTES and times_ist
                and times_ist[0].strftime("%H:%M") == "09:15" and times_ist[-1].strftime("%H:%M") == "15:39")
        if not full:
            continue
        highs = [r["high"] for r in rows if r["high"] is not None]
        lows = [r["low"] for r in rows if r["low"] is not None]
        profiles.append({
            "symbol": symbol, "option_type": "CE" if side == "CALL" else "PE",
            "date": day, "strike": strike, "open": rows[0]["open"],
            "high": max(highs) if highs else None, "low": min(lows) if lows else None,
            "close": rows[-1]["close"], "volume": sum((r["volume"] or 0.0) for r in rows),
            "oi": rows[-1]["oi"], "minutes": len(rows),
        })
    return profiles, duplicate_keys, conflict_keys


def _prices_match(profile, eod):
    for field in ("open", "high", "low", "close"):
        left, right = profile.get(field), eod.get(field)
        if left is None or right is None or abs(left - right) > PRICE_TOLERANCE:
            return False
    return True


def audit_expiry_identity(surface_blocks, fetch_bytes, expiry_code=1):
    """Cross-check a Dhan expiry selector against official daily contract OHLC; rows remain ephemeral."""
    if expiry_code not in (0, 1, 2):
        raise ValueError("Expiry code must be 0, 1 or 2.")
    profiles, duplicate_keys, conflict_keys = _extract_profiles(surface_blocks)
    dates = sorted({profile["date"] for profile in profiles})
    result = {
        "status": "BLOCKED_EOD_CROSSCHECK_NOT_RUN",
        "method": f"Exact-strike full-session Dhan OHLC aggregated in memory and matched to NSE UDiFF daily stock-option OHLC; expiryCode={expiry_code} is checked against active listed-expiry rank {expiry_code + 1}",
        "source": "NSE official F&O UDiFF daily bhavcopy archive",
        "source_url_template": NSE_URL,
        "raw_rows_persisted": False,
        "trade_dates_requested": len(dates), "trade_dates_downloaded": 0,
        "eligible_full_session_profiles": len(profiles), "unique_exact_contract_matches": 0,
        "ambiguous_profile_count": 0, "unmatched_profile_count": 0,
        "expiry_code_matches": 0, "expiry_selector_mismatches": 0,
        "supporting_volume_matches": 0, "supporting_oi_matches": 0,
        "distinct_matched_panels": 0, "duplicate_timestamp_strike_rows_deduplicated": duplicate_keys,
        "conflicting_duplicate_key_count": conflict_keys, "matched_expiry_counts": {}, "matched_expiry_rank_counts": {},
        "profiles_with_eod_contract_candidates": 0,
        "price_field_match_counts": {"open": 0, "high": 0, "low": 0, "close": 0},
        "price_field_match_histogram": {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0},
        "safe_source_errors": [],
    }
    if not dates:
        result["status"] = "BLOCKED_NO_FULL_SESSION_EXACT_STRIKE_PROFILES"
        return result
    nse_by_day = {}
    for day in dates:
        url = NSE_URL.format(date=day.replace("-", ""))
        try:
            nse_by_day[day] = parse_nse_bhavcopy(fetch_bytes(url, timeout=30))
            result["trade_dates_downloaded"] += 1
        except Exception as exc:
            result["safe_source_errors"].append({"date": day, "error_type": type(exc).__name__, "safe_message": " ".join(str(exc).split())[:200]})
    if result["safe_source_errors"]:
        result["status"] = "BLOCKED_NSE_EOD_SOURCE_FETCH_OR_SCHEMA_ERROR"
        return result

    matched_expiries = defaultdict(int)
    matched_expiry_ranks = defaultdict(int)
    matched_panels = set()
    field_match_counts = {"open": 0, "high": 0, "low": 0, "close": 0}
    field_match_histogram = defaultdict(int)
    profiles_with_candidates = 0
    unique_matches = ambiguous = unmatched = code_matches = selector_mismatches = 0
    volume_matches = oi_matches = 0
    for profile in profiles:
        day_rows = nse_by_day.get(profile["date"], [])
        same_symbol_day = [r for r in day_rows if r["symbol"] == profile["symbol"]]
        side_rows = [r for r in same_symbol_day if r["option_type"] == profile["option_type"]]
        candidates = [r for r in side_rows if r["strike"] == profile["strike"]]
        if candidates:
            profiles_with_candidates += 1
        field_flags = {
            field: any(profile.get(field) is not None and candidate.get(field) is not None
                       and abs(profile[field] - candidate[field]) <= PRICE_TOLERANCE for candidate in candidates)
            for field in ("open", "high", "low", "close")
        }
        for field, matched in field_flags.items():
            if matched:
                field_match_counts[field] += 1
        field_match_histogram[str(sum(field_flags.values()))] += 1
        price_candidates = [r for r in candidates if _prices_match(profile, r)]
        if len(price_candidates) != 1:
            if len(price_candidates) > 1:
                ambiguous += 1
            else:
                unmatched += 1
            continue
        selected = price_candidates[0]
        unique_matches += 1
        matched_expiries[selected["expiry"]] += 1
        matched_panels.add((profile["symbol"], profile["option_type"]))
        if selected.get("volume") is not None and abs(profile["volume"] - selected["volume"]) < 0.5:
            volume_matches += 1
        if profile.get("oi") is not None and selected.get("oi") is not None and abs(profile["oi"] - selected["oi"]) < 0.5:
            oi_matches += 1
        active_expiries = sorted({r["expiry"] for r in same_symbol_day if r["expiry"] >= profile["date"]})
        rank = active_expiries.index(selected["expiry"]) + 1 if selected["expiry"] in active_expiries else None
        if rank is not None:
            matched_expiry_ranks[str(rank)] += 1
        expected = active_expiries[expiry_code] if len(active_expiries) > expiry_code else None
        if expected is not None and selected["expiry"] == expected:
            code_matches += 1
        else:
            selector_mismatches += 1

    total = len(profiles)
    result.update({
        "unique_exact_contract_matches": unique_matches, "ambiguous_profile_count": ambiguous,
        "unmatched_profile_count": unmatched, "expiry_code_matches": code_matches,
        "expiry_selector_mismatches": selector_mismatches, "supporting_volume_matches": volume_matches,
        "supporting_oi_matches": oi_matches, "distinct_matched_panels": len(matched_panels),
        "matched_expiry_counts": dict(sorted(matched_expiries.items())),
        "matched_expiry_rank_counts": dict(sorted(matched_expiry_ranks.items(), key=lambda x:int(x[0]))),
        "profiles_with_eod_contract_candidates": profiles_with_candidates,
        "price_field_match_counts": field_match_counts,
        "price_field_match_histogram": {str(i):field_match_histogram.get(str(i), 0) for i in range(5)},
    })
    if (total >= 8 and unique_matches == total and code_matches == total and ambiguous == 0 and unmatched == 0
        and selector_mismatches == 0 and conflict_keys == 0 and len(matched_panels) >= 3 and len(dates) >= 3):
        result["status"] = f"PASS_EOD_RECONCILED_EXPIRY_CODE_{expiry_code}"
    elif unique_matches:
        result["status"] = "PARTIAL_EOD_EXPIRY_RECONCILIATION"
    else:
        result["status"] = "BLOCKED_EOD_EXPIRY_RECONCILIATION_INSUFFICIENT"
    return result
