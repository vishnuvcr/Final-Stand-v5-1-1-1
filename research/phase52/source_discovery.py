#!/usr/bin/env python3
"""Discover candidate public research sources; save metadata only, never treat claims as performance evidence."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research" / "phase52" / "results" / "source_discovery"
USER_AGENT = "FinalStand-Phase52-ResearchBot/1.0 (+https://github.com/vishnuvcr/Final-Stand-v5-1-1-1)"
HF_QUERIES = [
    "india index options", "NIFTY options intraday", "NSE options historical",
    "India VIX", "NIFTY option chain open interest"
]
GH_QUERIES = [
    "NIFTY options backtest", "India VIX options strategy",
    "NIFTY option chain open interest Greeks", "Indian index options strategy",
    "options backtesting engine India"
]
YT_QUERIES = [
    "NIFTY options India VIX strategy", "NIFTY options Greeks open interest strategy",
    "Profit Breakout India VIX options strategy", "iron condor ratio spread NIFTY"
]


def request_json(url: str, headers: dict[str, str] | None = None) -> Any:
    hdrs = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


def run_query(label: str, query: str, url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
    try:
        payload = request_json(url, headers)
        return {"source_type": label, "query": query, "query_url": url, "status": "OK", "payload": payload}
    except urllib.error.HTTPError as exc:
        return {"source_type": label, "query": query, "query_url": url, "status": "HTTP_ERROR", "http_status": exc.code}
    except Exception as exc:
        return {"source_type": label, "query": query, "query_url": url, "status": "ERROR", "error_type": type(exc).__name__, "error": str(exc)[:300]}


def discover() -> dict[str, Any]:
    hf_token = os.environ.get("HF_TOKEN", "")
    gh_token = os.environ.get("GITHUB_TOKEN", "")
    yt_key = os.environ.get("YOUTUBE_API_KEY", "")
    results: list[dict[str, Any]] = []
    hf_headers = {"Authorization": "Bearer " + hf_token} if hf_token else None
    gh_headers = {"Authorization": "Bearer " + gh_token} if gh_token else None

    for query in HF_QUERIES:
        url = "https://huggingface.co/api/datasets?" + urllib.parse.urlencode({"search": query, "limit": 20, "sort": "downloads", "direction": "-1"})
        raw = run_query("huggingface_dataset_search", query, url, hf_headers)
        payload = raw.pop("payload", None)
        if isinstance(payload, list):
            raw["sources"] = [{
                "id": item.get("id"), "last_modified": item.get("lastModified"),
                "downloads": item.get("downloads"), "likes": item.get("likes"),
                "tags": item.get("tags", [])[:15],
                "url": "https://huggingface.co/datasets/" + str(item.get("id", "")),
            } for item in payload]
            raw["result_count"] = len(payload)
        results.append(raw)

    for query in GH_QUERIES:
        url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode({"q": query, "per_page": 20, "sort": "updated"})
        raw = run_query("github_repository_search", query, url, gh_headers)
        payload = raw.pop("payload", None)
        if isinstance(payload, dict):
            items = payload.get("items", [])
            raw["sources"] = [{
                "full_name": item.get("full_name"), "description": (item.get("description") or "")[:400],
                "default_branch": item.get("default_branch"), "pushed_at": item.get("pushed_at"),
                "stars": item.get("stargazers_count"), "license": (item.get("license") or {}).get("spdx_id"),
                "url": item.get("html_url"),
            } for item in items]
            raw["result_count"] = len(items)
        results.append(raw)

    if yt_key:
        for query in YT_QUERIES:
            url = "https://www.googleapis.com/youtube/v3/search?" + urllib.parse.urlencode({
                "part": "snippet", "type": "video", "maxResults": 25, "q": query,
                "key": yt_key, "order": "relevance"
            })
            raw = run_query("youtube_video_search", query, url)
            payload = raw.pop("payload", None)
            if isinstance(payload, dict):
                items = payload.get("items", [])
                raw["sources"] = [{
                    "video_id": item.get("id", {}).get("videoId"),
                    "title": (item.get("snippet", {}).get("title") or "")[:300],
                    "channel": item.get("snippet", {}).get("channelTitle"),
                    "published_at": item.get("snippet", {}).get("publishedAt"),
                    "url": "https://www.youtube.com/watch?v=" + str(item.get("id", {}).get("videoId", "")),
                } for item in items]
                raw["result_count"] = len(items)
            results.append(raw)
    else:
        results.append({
            "source_type": "youtube_video_search", "query": "all registered YouTube queries",
            "status": "NOT_RUN", "reason": "YOUTUBE_API_KEY secret is not configured. Existing Phase 46 video ledger remains available; do not claim a fresh full-channel crawl."
        })

    return {
        "schema_version": "1.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "SOURCE_DISCOVERY_ONLY_NOT_BACKTEST_EVIDENCE",
        "credentials_present": {
            "HF_TOKEN": bool(hf_token),
            "GITHUB_TOKEN": bool(gh_token),
            "YOUTUBE_API_KEY": bool(yt_key),
        },
        "queries": results,
        "interpretation": "Search results are unverified discovery leads. A candidate only enters numerical testing after exact rules, data provenance, licensing and timestamp/contract coverage are audited. Do not treat stars, downloads, video views or author P&L claims as evidence."
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report = discover()
    day = report["timestamp_utc"][:10]
    (OUT / "latest.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / (day + ".json")).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ledger = OUT / "source_ledger.jsonl"
    seen: set[str] = set()
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            try:
                item = json.loads(line)
                seen.add(item.get("dedupe_key", ""))
            except json.JSONDecodeError:
                continue
    added = 0
    with ledger.open("a", encoding="utf-8") as fh:
        for query in report["queries"]:
            for source in query.get("sources", []):
                url = source.get("url", "")
                if not url:
                    continue
                key = query["source_type"] + "|" + url
                if key in seen:
                    continue
                fh.write(json.dumps({
                    "dedupe_key": key, "first_seen_utc": report["timestamp_utc"],
                    "query": query.get("query"), "source_type": query["source_type"],
                    "source": source, "evidence_grade": "DISCOVERY_LEAD_NOT_VALIDATED"
                }, ensure_ascii=False, sort_keys=True) + "\n")
                seen.add(key)
                added += 1
    report["new_unique_source_leads_added"] = added
    (OUT / "latest.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "query_count": len(report["queries"]),
        "source_leads_added": added,
        "credentials_present": report["credentials_present"],
        "output": str(OUT / "latest.json"),
    }, indent=2))
    failed = [r for r in report["queries"] if r["status"] in {"ERROR", "HTTP_ERROR"}]
    return 0 if len(failed) < len(report["queries"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
