#!/usr/bin/env python3
"""Bounded Phase 53 metadata-only source and pinned-file coverage audit.

Does not download market bars, request brokerage credentials, or run strategy P&L.
HTTP failures are preserved as unknown/inaccessible; they are not silently called
missing data. Output contains public metadata, paths, hashes/ETags and status only.
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "research" / "phase53" / "sources.json"
DEFAULT_OUT = ROOT / "results" / "phase53" / "source_coverage_audit" / "report.json"
USER_AGENT = "Final-Stand-Phase53-Research/1.0 (metadata-only; contact repository owner)"
MAX_METADATA_BYTES = 2_000_000


def load_registry(path: Path = REGISTRY) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj.get("sources"), list) or not obj["sources"]:
        raise ValueError("source registry must contain a non-empty sources list")
    dataset = obj.get("parent_dataset", {})
    if not dataset.get("revision") or not dataset.get("required_files"):
        raise ValueError("parent dataset revision and required_files are mandatory")
    ids = [s.get("id") for s in obj["sources"]]
    if any(not item for item in ids) or len(ids) != len(set(ids)):
        raise ValueError("source IDs must be non-empty and unique")
    return obj


def assess_inventory(items: Iterable[dict[str, Any]], required_paths: list[str]) -> dict[str, Any]:
    """Assess a known metadata listing; never treat a failed listing as an empty list."""
    rows = list(items)
    by_path: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    for item in rows:
        name = item.get("path") or item.get("name") or item.get("rfilename")
        if not isinstance(name, str) or not name:
            continue
        # Normalize API responses that list only paths relative to the requested folder.
        normalized = name.lstrip("/")
        if normalized in by_path and normalized not in duplicates:
            duplicates.append(normalized)
        else:
            by_path[normalized] = item
    # Permit either full dataset-relative paths or basename results from a folder listing.
    present: list[str] = []
    missing: list[str] = []
    metadata: list[dict[str, Any]] = []
    for required in required_paths:
        basename = required.rsplit("/", 1)[-1]
        candidate = by_path.get(required) or by_path.get(basename)
        if candidate is None:
            candidate = next((v for k, v in by_path.items() if k.endswith("/" + required) or k.endswith("/" + basename)), None)
        if candidate is None:
            missing.append(required)
        else:
            present.append(required)
            lfs = candidate.get("lfs") if isinstance(candidate.get("lfs"), dict) else {}
            metadata.append({
                "path": required,
                "listed_path": candidate.get("path") or candidate.get("name") or candidate.get("rfilename"),
                "size_bytes": candidate.get("size"),
                "oid": candidate.get("oid"),
                "lfs_oid": lfs.get("oid"),
                "lfs_size": lfs.get("size"),
            })
    return {
        "listing_complete": True,
        "required_count": len(required_paths),
        "present_count": len(present),
        "missing_count": len(missing),
        "present_paths": present,
        "missing_paths": missing,
        "file_metadata": metadata,
        "duplicate_list_entries": duplicates,
    }


def request_url(url: str, method: str = "GET", token: str | None = None,
                timeout: float = 18.0, read_limit: int = 128_000) -> dict[str, Any]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/html, application/pdf, */*",
    }
    if token and "huggingface.co" in url:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers, method=method)
    started = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read(read_limit) if method != "HEAD" else b""
            return {
                "url": url,
                "http_status": int(response.status),
                "reachable": 200 <= int(response.status) < 400,
                "content_type": response.headers.get("Content-Type"),
                "content_length": response.headers.get("Content-Length"),
                "etag": response.headers.get("ETag"),
                "last_modified": response.headers.get("Last-Modified"),
                "body_prefix_bytes": len(body),
                "body_sha256_prefix": __import__("hashlib").sha256(body).hexdigest() if body else None,
                "elapsed_ms": int((time.monotonic() - started) * 1000),
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        return {
            "url": url, "http_status": int(exc.code), "reachable": False,
            "content_type": exc.headers.get("Content-Type"),
            "content_length": exc.headers.get("Content-Length"),
            "etag": exc.headers.get("ETag"), "last_modified": exc.headers.get("Last-Modified"),
            "body_prefix_bytes": 0, "body_sha256_prefix": None,
            "elapsed_ms": int((time.monotonic() - started) * 1000),
            "error": "HTTP_ERROR",
        }
    except Exception as exc:
        return {
            "url": url, "http_status": None, "reachable": False,
            "content_type": None, "content_length": None, "etag": None, "last_modified": None,
            "body_prefix_bytes": 0, "body_sha256_prefix": None,
            "elapsed_ms": int((time.monotonic() - started) * 1000),
            "error": type(exc).__name__ + ": " + str(exc)[:240],
        }


def json_request(url: str, token: str | None = None) -> tuple[dict[str, Any], Any | None]:
    result = request_url(url, "GET", token, read_limit=MAX_METADATA_BYTES)
    if not result["reachable"]:
        return result, None
    # Re-read only a metadata JSON endpoint; no market-price files are requested.
    try:
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        if token and "huggingface.co" in url:
            headers["Authorization"] = "Bearer " + token
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=18.0) as response:
            raw = response.read(MAX_METADATA_BYTES + 1)
        if len(raw) > MAX_METADATA_BYTES:
            result["metadata_parse_error"] = "metadata exceeds size limit"
            return result, None
        obj = json.loads(raw.decode("utf-8"))
        result["metadata_parsed"] = True
        return result, obj
    except Exception as exc:
        result["metadata_parse_error"] = type(exc).__name__ + ": " + str(exc)[:240]
        return result, None


def listed_tree(repo_id: str, revision: str, token: str | None) -> tuple[dict[str, Any], list[dict[str, Any]] | None]:
    # Query the option and index directories independently, then combine metadata
    # listings only when each returned JSON successfully. Fallback to a recursive
    # root listing only if both directory endpoints are inaccessible.
    urls = [
        f"https://huggingface.co/api/datasets/{repo_id}/tree/{revision}/options/NIFTY?recursive=false&expand=true",
        f"https://huggingface.co/api/datasets/{repo_id}/tree/{revision}/index?recursive=false&expand=true",
    ]
    attempted = []
    combined: list[dict[str, Any]] = []
    success_count = 0
    for url in urls:
        meta, data = json_request(url, token)
        attempted.append(meta)
        if isinstance(data, list):
            combined.extend(data)
            success_count += 1
    if success_count:
        return {
            "attempts": attempted,
            "successful_url_count": success_count,
            "expected_directory_count": len(urls),
            "listing_complete": success_count == len(urls),
            "http_status": 200,
        }, combined
    root_url = f"https://huggingface.co/api/datasets/{repo_id}/tree/{revision}?recursive=true&expand=false"
    meta, data = json_request(root_url, token)
    attempted.append(meta)
    if isinstance(data, list):
        return {
            "attempts": attempted,
            "successful_url_count": 1,
            "expected_directory_count": len(urls),
            "listing_complete": True,
            "root_listing_fallback": True,
            "http_status": meta.get("http_status"),
        }, data
    return {
        "attempts": attempted,
        "successful_url_count": 0,
        "expected_directory_count": len(urls),
        "listing_complete": False,
        "http_status": None,
    }, None

def source_probe(source: dict[str, Any], token: str | None) -> dict[str, Any]:
    result = request_url(source["url"], "GET", token, read_limit=24_000)
    result.update({
        "source_id": source["id"],
        "source_name": source["name"],
        "source_class": source["class"],
        "claimed_granularity": source.get("expected_granularity", "not specified"),
        "license": source.get("license", "not established by metadata probe"),
    })
    if source.get("api_url"):
        meta, data = json_request(source["api_url"], token)
        result["api_metadata_probe"] = {
            "url": meta.get("url"),
            "http_status": meta.get("http_status"),
            "reachable": meta.get("reachable"),
            "metadata_parsed": meta.get("metadata_parsed", False),
            "metadata_error": meta.get("metadata_parse_error"),
            "top_level_fields": sorted(data.keys())[:60] if isinstance(data, dict) else None,
            "dataset_sha": data.get("sha") if isinstance(data, dict) else None,
            "license": ((data.get("cardData") or {}).get("license")) if isinstance(data, dict) else None,
        }
    return result


def audit(registry: dict[str, Any]) -> dict[str, Any]:
    token = os.environ.get("HF_TOKEN") or None
    sources = registry["sources"]
    source_checks = [source_probe(source, token) for source in sources]
    parent = registry["parent_dataset"]
    repo_id = parent["repo"]
    revision = parent["revision"]
    required = list(parent["required_files"])

    # HEAD requests check exact pinned file paths and avoid transferring market data.
    file_checks = []
    for path in required:
        url = f"https://huggingface.co/datasets/{repo_id}/resolve/{revision}/{path}"
        info = request_url(url, "HEAD", token, timeout=25.0)
        file_checks.append({
            "path": path,
            "http_status": info["http_status"],
            "reachable": info["reachable"],
            "content_length": info["content_length"],
            "etag": info["etag"],
            "last_modified": info["last_modified"],
            "error": info["error"],
            "bytes_transferred": 0,
        })

    pinned_revision_url = f"https://huggingface.co/api/datasets/{repo_id}/revision/{revision}"
    revision_meta, revision_data = json_request(pinned_revision_url, token)
    revision_confirmed = (
        isinstance(revision_data, dict)
        and str(revision_data.get("sha", "")).lower() == revision.lower()
    )
    hf_listing_meta, hf_listing = listed_tree(repo_id, revision, token)
    inventory = None
    if hf_listing is not None:
        inventory = assess_inventory(hf_listing, required)

    file_statuses = [row["http_status"] for row in file_checks]
    known = [x for x in file_statuses if isinstance(x, int)]
    found = sum(1 for row in file_checks if row["http_status"] and 200 <= row["http_status"] < 400)
    not_found = sum(1 for row in file_checks if row["http_status"] == 404)
    unknown = len(file_checks) - len(known)
    real_quote_source = False  # None in the registered public sources advertises a free full historical quote/depth archive.
    all_hf = next((s for s in source_checks if s.get("source_id") == "hf_pinned"), {})
    api_hf = all_hf.get("api_metadata_probe", {})
    dataset_revision_confirmed = revision_confirmed
    metadata_completeness = sum(1 for s in source_checks if s.get("http_status") is not None)
    decision = "SOURCE_INVENTORY_COMPLETE_BUT_INTRADAY_QUOTE_NO_GO"
    if found == len(required):
        data_status = "ALL_REQUIRED_PATHS_HEAD_ACCESSIBLE"
    elif found > 0:
        data_status = "PARTIAL_REQUIRED_PATH_COVERAGE"
    elif not_found == len(required):
        data_status = "REQUIRED_PATHS_NOT_FOUND_AT_PINNED_REVISION"
    else:
        data_status = "REQUIRED_PATH_COVERAGE_UNKNOWN_OR_INACCESSIBLE"
    if unknown and not_found == 0 and found < len(required):
        decision = "PARTIAL_AUDIT_ACCESS_BLOCKED_REQUIRES_RETRY"
    return {
        "phase_id": registry["phase_id"],
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "COMPLETED_SOURCE_METADATA_AUDIT",
        "source_data_downloaded": False,
        "market_prices_or_raw_bars_committed": False,
        "strategy_backtest_run": False,
        "holdout_used": False,
        "dataset": {
            "repo": repo_id,
            "pinned_revision": revision,
            "declared_license": parent.get("license"),
            "required_path_count": len(required),
            "head_accessible_count": found,
            "http_404_count": not_found,
            "unknown_or_inaccessible_count": unknown,
            "coverage_status": data_status,
            "revision_confirmed_by_metadata": dataset_revision_confirmed,
            "revision_metadata_probe": {
                "url": revision_meta.get("url"),
                "http_status": revision_meta.get("http_status"),
                "reachable": revision_meta.get("reachable"),
                "returned_sha": revision_data.get("sha") if isinstance(revision_data, dict) else None,
                "error": revision_meta.get("error") or revision_meta.get("metadata_parse_error"),
            },
            "required_file_checks": file_checks,
            "tree_listing": {
                "status": "AVAILABLE" if hf_listing is not None else "INACCESSIBLE_OR_UNSUPPORTED",
                "meta": hf_listing_meta,
                "inventory_assessment": inventory,
            },
        },
        "sources": source_checks,
        "execution_quality": {
            "free_full_history_bid_ask_archive_confirmed": real_quote_source,
            "ohlc_range_is_bid_ask_spread": False,
            "decision": "NO_GO_FOR_TRUE_HISTORICAL_SPREAD_DEPTH_VALIDATION_FROM_REGISTERED_FREE_SOURCES",
            "reason": "The pinned source documents OHLCV+OI, not quote/depth. NSE/BSE pages include daily reports and product-specific feeds; the inspected public repositories distinguish samples or credentialed broker access from anonymous full-history data.",
        },
        "summary": {
            "source_registry_count": len(sources),
            "source_pages_with_http_status": metadata_completeness,
            "required_paths": len(required),
            "required_paths_accessible_by_head": found,
            "required_paths_404": not_found,
            "required_paths_unknown": unknown,
            "decision": decision,
            "strategy_efficacy_claim": False,
            "recommendation": "Freeze Phase 52 result and continue only with source coverage remediation; do not loosen gates or promote a strategy from 1/480 executions.",
        },
        "acceptance_gates": {
            "metadata_probes_completed": True,
            "pinned_file_inventory_complete": found == len(required),
            "exact_480_row_ledger_reconciled_in_this_phase": False,
            "free_timestamp_aligned_bid_ask_or_depth_verified": False,
            "80_percent_row_coverage_for_later_pnl_phase": False,
            "holdout_untouched": True,
        },
        "limitations": [
            "HEAD accessibility proves a pinned path resolves, not that its rows are correct or contain every contract/time.",
            "The source inventory did not download market files; exact row-level OHLC/OI checks require cached local partitions and the version-matched 480-row ledger.",
            "A 403/timeout/API incompatibility is unknown access, not a missing source file.",
            "Daily EOD OI and participant reports cannot be forward-filled into intraday signals.",
            "No full historical bid/ask/depth source has been verified as free and lawful in the registered candidates.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--self-test-only", action="store_true")
    args = parser.parse_args()
    registry = load_registry(args.registry)
    if args.self_test_only:
        sample = assess_inventory([{"path": "options/NIFTY/2021-05-27.parquet", "size": 10}], [
            "options/NIFTY/2021-05-27.parquet", "index/NIFTY.parquet"
        ])
        assert sample["present_count"] == 1 and sample["missing_count"] == 1
        print(json.dumps({"self_test": "PASS", "source_count": len(registry["sources"]),
                          "required_path_count": len(registry["parent_dataset"]["required_files"])}))
        return 0
    report = audit(registry)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"], "output": str(args.output.resolve().relative_to(ROOT.resolve())),
        "required_paths": report["summary"]["required_paths"],
        "head_accessible": report["summary"]["required_paths_accessible_by_head"],
        "head_404": report["summary"]["required_paths_404"],
        "unknown": report["summary"]["required_paths_unknown"],
        "decision": report["summary"]["decision"],
        "source_downloaded": False, "strategy_backtest_run": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
