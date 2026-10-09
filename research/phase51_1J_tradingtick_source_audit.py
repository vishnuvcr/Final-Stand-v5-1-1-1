from __future__ import annotations
import asyncio, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urljoin
from playwright.async_api import async_playwright

ROOT = Path("results/phase51/phase51_1J_tradingtick")
ROOT.mkdir(parents=True, exist_ok=True)
DEBUG = ROOT / "responses"
DEBUG.mkdir(exist_ok=True)
BASE = "https://tradingtick.in"
PAGES = {
    "historical_chain": f"{BASE}/nifty/download-nifty-option-chain-historical-data.php",
    "expired_chart": f"{BASE}/nifty/nifty-option-price-charts.php",
    "chart_data": f"{BASE}/nifty/nifty-option-charts-historical-data.php",
}
TARGETS = ["2026-07-28", "2026-08-04"]
manifest = {
    "audit": "Phase 51-1J TradingTick public-source audit",
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "source": BASE, "targets": TARGETS, "classification": "PENDING",
    "pnl_eligible": False, "pages": {},
    "notes": [
        "Ordinary public browser interaction only; no access-control bypass.",
        "Page metadata/date selectors do not prove target-session raw-row coverage.",
        "No P&L is calculated by this audit."
    ],
}
network_all, files_seen = [], []

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def target_hit(vals, date):
    s = " ".join(str(x) for x in vals)
    yyyy, mm, dd = date.split("-")
    patterns = [date, f"{yyyy}/{mm}/{dd}", f"{yyyy}{mm}{dd}", f"{dd}-{mm}-{yyyy}", f"{dd}/{mm}/{yyyy}"]
    return any(p in s for p in patterns)

async def select_snapshot(page):
    js = """els => Array.from(els, (e,i) => ({
      index:i, id:e.id||"", name:e.name||"", aria:e.getAttribute("aria-label")||"",
      labels:[], parentText:(e.parentElement && e.parentElement.innerText || "").trim().slice(0,160),
      disabled:!!e.disabled, value:e.value||"",
      options:Array.from(e.options).map(o => ({text:(o.textContent||"").trim(),value:o.value,disabled:!!o.disabled})).slice(0,400)
    }))"""
    return await page.locator("select").evaluate_all(js)

async def page_state(page):
    return await page.evaluate("""() => ({
      title: document.title, url: location.href,
      forms: Array.from(document.forms).map(f => ({action:f.action,method:f.method,id:f.id,name:f.name,
        inputs:Array.from(f.elements).map(e=>({tag:e.tagName,id:e.id||'',name:e.name||'',type:e.type||'',value:(e.value||'').slice(0,120)}))})),
      headings: Array.from(document.querySelectorAll('h1,h2,h3')).map(e=>(e.innerText||'').trim()).filter(Boolean).slice(0,50),
      buttons: Array.from(document.querySelectorAll('button,input[type=submit],a')).map(e=>({
        tag:e.tagName,text:(e.innerText||e.value||e.getAttribute('aria-label')||'').trim().slice(0,100),
        href:e.href||'',id:e.id||'',name:e.name||'',type:e.type||''}))
        .filter(e=>/download|export|csv|excel|previous|next|apply|search|show|load/i.test(e.text+' '+e.href+' '+e.id+' '+e.name)).slice(0,100),
      bodyText:(document.body?.innerText||'').slice(0,5000),
      scripts:Array.from(document.scripts).map(s=>({src:s.src||'',inline:(s.src?'':(s.textContent||'').slice(0,25000))})).slice(0,100)
    })""")

async def try_change(page, target):
    attempts=[]
    for _ in range(7):
        infos=await select_snapshot(page)
        changed=False
        for info in infos:
            ident=(info.get("id","")+" "+info.get("name","")+" "+info.get("aria","")+" "+" ".join(info.get("labels",[]))+" "+info.get("parentText","")).lower()
            opts=info.get("options",[])
            if not opts or info.get("disabled"): continue
            candidates=[]
            if re.search(r"year|ex.?year|expiry.?yr|exp.?year",ident):
                candidates=[o for o in opts if o["value"]=="2026" or o["text"].strip()=="2026"]
            elif re.search(r"month|ex.?month|expiry.?month",ident):
                _,mm,_=target.split("-")
                mon={"07":["July","Jul","7","07"],"08":["August","Aug","8","08"]}[mm]
                candidates=[o for o in opts if o["text"].strip().lower() in [x.lower() for x in mon] or o["value"].strip() in mon]
            elif re.search(r"expiry|expdate|exp_date|expir",ident):
                candidates=[o for o in opts if target_hit([o["value"],o["text"]],target)]
            elif re.search(r"(^|[^a-z])date([^a-z]|$)|trade.?date|session",ident):
                candidates=[o for o in opts if target_hit([o["value"],o["text"]],target)]
            if not candidates:
                for o in opts:
                    if target_hit([o["value"],o["text"]],target):
                        candidates=[o]; break
            if candidates:
                cand=candidates[0]
                if cand["value"] != info.get("value"):
                    try:
                        await page.locator("select").nth(info["index"]).select_option(value=cand["value"],timeout=2500)
                        attempts.append({"select_index":info["index"],"id":info["id"],"name":info["name"],
                          "label":info.get("labels"),"selected":{"text":cand["text"],"value":cand["value"]},"target":target})
                        await page.wait_for_timeout(900)
                        changed=True
                        break
                    except Exception as e:
                        attempts.append({"select_index":info["index"],"error":str(e)[:200],"target":target})
        if not changed: break
    infos=await select_snapshot(page)
    target_options=[]
    for x in infos:
        opts=x.get("options",[])
        target_options.append({"index":x["index"],"id":x["id"],"name":x["name"],"labels":x.get("labels"),
          "selected":x.get("value"),"contains_target":target_hit([v for o in opts for v in (o["value"],o["text"])],target),
          "target_options":[o for o in opts if target_hit([o["value"],o["text"]],target)]})
    return {"attempts":attempts,"selects_after":infos,"target_option_scan":target_options}

def script_endpoints(js):
    out=set()
    for pat in [
        r"""['"]([^'"]*(?:\.php|\.json|/api/)[^'"]*)['"]""",
        r"""(?:url|action|endpoint|fetch|ajax)\s*[:=(]\s*['"]([^'"]+)['"]""",
    ]:
        for s in re.findall(pat,js,flags=re.I):
            if len(s)<300 and (".php" in s or ".json" in s or "/api/" in s or "fetch" in s.lower()):
                out.add(s)
    return sorted(out)[:200]

async def main():
  async with async_playwright() as p:
    browser=await p.chromium.launch(headless=True)
    context=await browser.new_context(accept_downloads=True,viewport={"width":1440,"height":1200})
    for slug,url in PAGES.items():
      page=await context.new_page()
      local_net=[]
      def on_request(req):
        try:
          rec={"event":"request","page":slug,"url":req.url[:1000],"method":req.method,"resource_type":req.resource_type}
          if req.method not in ("GET","HEAD") and req.post_data: rec["post_data_prefix"]=req.post_data[:1200]
          local_net.append(rec); network_all.append(rec)
        except Exception: pass
      async def on_response(resp):
        try:
          req=resp.request; headers=await resp.all_headers(); ctype=headers.get("content-type","")
          rec={"event":"response","page":slug,"url":resp.url[:1000],"status":resp.status,
               "resource_type":req.resource_type,"content_type":ctype,"content_length":headers.get("content-length","")}
          local_net.append(rec); network_all.append(rec)
          if resp.status==200 and urlparse(resp.url).netloc==urlparse(BASE).netloc and (req.resource_type in ("xhr","fetch") or any(x in ctype.lower() for x in ["application/json","text/csv","spreadsheet","excel","octet-stream"])):
            body=await resp.body(); rec["actual_bytes"]=len(body); rec["sha256"]=sha(body)
            if len(body)<=12000000 and (req.resource_type in ("xhr","fetch") or "json" in ctype.lower() or "csv" in ctype.lower()):
              ext=".json" if "json" in ctype.lower() else ".csv" if "csv" in ctype.lower() else ".txt"
              nm=hashlib.sha256((slug+resp.url).encode()).hexdigest()[:20]+ext
              (DEBUG/nm).write_bytes(body)
              files_seen.append({"page":slug,"url":resp.url,"path":str(DEBUG/nm),"bytes":len(body),
                                 "sha256":sha(body),"content_type":ctype})
              try:
                obj=json.loads(body.decode("utf-8",errors="replace"))
                if isinstance(obj,dict): rec["json_top_keys"]=list(obj.keys())[:100]
                elif isinstance(obj,list):
                  rec["json_is_list"]=True; rec["json_items"]=len(obj)
                  rec["json_first_item_keys"]=list(obj[0].keys())[:100] if obj and isinstance(obj[0],dict) else None
              except Exception: rec["body_preview"]=body[:180].decode("utf-8",errors="replace")
        except Exception: pass
      page.on("request",on_request); page.on("response",on_response)
      entry={"url":url,"navigation_status":None,"error":None,"initial_state":{},"selectors_by_target":{},"request_count":0}
      try:
        resp=await page.goto(url,wait_until="domcontentloaded",timeout=45000)
        entry["navigation_status"]=resp.status if resp else None
        try: await page.wait_for_load_state("networkidle",timeout=15000)
        except Exception: pass
        await page.wait_for_timeout(1800)
        entry["initial_state"]=await page_state(page)
        entry["initial_selects"]=await select_snapshot(page)
        script_reports=[]
        for s in entry["initial_state"].get("scripts",[])[:100]:
          if s.get("src"):
            abs_url=urljoin(url,s["src"])
            if urlparse(abs_url).netloc != urlparse(BASE).netloc: continue
            try:
              r=await context.request.get(abs_url,timeout=12000)
              if r.ok:
                js=await r.text()
                script_reports.append({"url":abs_url,"status":r.status,"bytes":len(js.encode()),"sha256":sha(js.encode()),"endpoints":script_endpoints(js)})
            except Exception as e: script_reports.append({"url":abs_url,"error":str(e)[:180]})
          elif s.get("inline"):
            js=s["inline"]
            script_reports.append({"inline":True,"bytes":len(js.encode()),"sha256":sha(js.encode()),"endpoints":script_endpoints(js)})
        entry["scripts"]=script_reports
        for target in TARGETS:
          # Reset to a fresh page: cascading selectors must not inherit July state when checking August.
          await page.goto(url,wait_until="domcontentloaded",timeout=45000)
          try: await page.wait_for_load_state("networkidle",timeout=12000)
          except Exception: pass
          await page.wait_for_timeout(650)
          entry["selectors_by_target"][target]=await try_change(page,target)
          try: await page.wait_for_load_state("networkidle",timeout=7000)
          except Exception: pass
          await page.wait_for_timeout(650)
          # Select one actual strike in each historical-chart page to trigger its normal chart-data request.
          if slug in ("expired_chart","chart_data"):
            try:
              snap=await select_snapshot(page)
              strike_sel=next((x for x in snap if re.search(r"strike",x.get("id","")+" "+x.get("name",""))),None)
              if strike_sel:
                valid=[]
                for opt in strike_sel.get("options",[]):
                  try: valid.append((abs(float(opt["value"])-24000.0),opt))
                  except Exception: pass
                if valid:
                  chosen=sorted(valid,key=lambda z:z[0])[0][1]
                  before=len(local_net)
                  await page.locator("select").nth(strike_sel["index"]).select_option(value=chosen["value"],timeout=3000)
                  try: await page.wait_for_load_state("networkidle",timeout=7000)
                  except Exception: pass
                  await page.wait_for_timeout(1800)
                  entry["selectors_by_target"][target]["selected_chart_test_contract"]={"expiry":target,"option":"CE","strike":chosen["value"],"visible_strikes":len(valid)}
                  entry["selectors_by_target"][target]["requests_after_strike_selection"]=local_net[before:]
                else:
                  entry["selectors_by_target"][target]["selected_chart_test_contract"]={"status":"NO_STRIKE_OPTIONS"}
            except Exception as e:
              entry["selectors_by_target"][target]["chart_strike_test_error"]=str(e)[:300]
          entry["selectors_by_target"][target]["visible_tables"]=await page.locator("table").evaluate_all("""ts => ts.slice(0,15).map(t => ({
            headers:Array.from(t.querySelectorAll('thead th')).map(e=>(e.innerText||'').trim()),
            rows:Array.from(t.querySelectorAll('tr')).slice(0,5).map(r=>(r.innerText||'').trim().slice(0,500)),
            row_count:t.querySelectorAll('tr').length}))""")
          entry["selectors_by_target"][target]["visible_text_excerpt"]=(await page.locator("body").inner_text())[:1800]
        entry["request_count"]=len(local_net)
      except Exception as e:
        entry["error"]=str(e)[:1000]; entry["request_count"]=len(local_net)
      manifest["pages"][slug]=entry
      await page.close()
    manifest["network_events"]=len(network_all)
    manifest["same_origin_data_responses"]=files_seen
    any_target_option=False
    any_intraday_payload=False
    eod_hint=False
    for slug,pdata in manifest["pages"].items():
      if slug=="historical_chain":
        blob=json.dumps(pdata).lower()
        if "end-of-day" in blob or "eod" in blob: eod_hint=True
      for scan in pdata.get("selectors_by_target",{}).values():
        if any(x.get("contains_target") for x in scan.get("target_option_scan",[])): any_target_option=True
    target_presence={}
    for target in TARGETS:
      presence={"expiry_selector":False,"session_date_selector":False,"chart_expiry_selector":False}
      for slug,pdata in manifest["pages"].items():
        for sc in pdata.get("selectors_by_target",{}).get(target,{}).get("target_option_scan",[]):
          ident=(sc.get("id","")+" "+sc.get("name","")).lower()
          if sc.get("contains_target") and ("expiry" in ident or "exp" in ident): presence["expiry_selector"]=True
          if sc.get("contains_target") and ("date" in ident or "session" in ident): presence["session_date_selector"]=True
          if sc.get("contains_target") and slug in ("expired_chart","chart_data"): presence["chart_expiry_selector"]=True
      target_presence[target]=presence
    response_reviews=[]
    for f in files_seen:
      review={"page":f["page"],"url":f["url"],"bytes":f["bytes"],"sha256":f["sha256"],"content_type":f["content_type"]}
      if f["path"].endswith((".csv",".json")):
        try:
          obj=json.loads(Path(f["path"]).read_text(errors="ignore"))
          review["top_level_type"]=type(obj).__name__
          if isinstance(obj,dict):
            review["top_level_keys"]=list(obj.keys())[:80]
            rows=obj.get("data")
            if isinstance(rows,list):
              review["row_count"]=len(rows)
              review["row_keys"]=list(rows[0].keys())[:80] if rows and isinstance(rows[0],dict) else []
              if rows and isinstance(rows[0],dict):
                review["first_row_sample"]={k:rows[0][k] for k in list(rows[0])[:18]}
          elif isinstance(obj,list):
            review["row_count"]=len(obj)
            review["first_row_keys"]=list(obj[0].keys())[:80] if obj and isinstance(obj[0],dict) else []
          raw=json.dumps(obj,ensure_ascii=False)
          has_iso=bool(re.search(r"20\\d{2}[-/]\\d{2}[-/]\\d{2}[ T]\\d{2}:\\d{2}",raw))
          hhmm=bool(re.search(r'"(?:0[9]|1[0-5]):[0-5]\\d(?::[0-5]\\d)?"',raw))
          keys=set(review.get("top_level_keys",[]))|set(review.get("row_keys",[]))|set(review.get("first_row_keys",[]))
          time_keys=any(str(k).lower() in {"timestamp","datetime","time","times","labels","x"} for k in keys)
          review["contains_iso_intraday_timestamp"]=has_iso
          review["contains_clock_time_label"]=hhmm
          review["has_time_axis_keys"]=time_keys
          if has_iso or hhmm or time_keys: any_intraday_payload=True
        except Exception as e: review["parse_error"]=str(e)[:200]
      response_reviews.append(review)
    manifest["response_reviews"]=response_reviews
    manifest["target_presence_by_control"]=target_presence
    manifest["target_date_selectable_in_any_control"]=any_target_option
    manifest["intraday_timestamp_in_observed_data_response"]=any_intraday_payload
    if any_intraday_payload: manifest["classification"]="INTRADAY_PAYLOAD_CANDIDATE_REQUIRES_RAW_COVERAGE_REVIEW"
    elif any_target_option: manifest["classification"]="DATE_VISIBLE_DATA_NOT_VERIFIED"
    elif eod_hint: manifest["classification"]="EOD_CONTEXT_ONLY_OR_RAW_DOWNLOAD_UNVERIFIED"
    else: manifest["classification"]="PUBLIC_PAGE_ACCESSIBLE_RAW_TARGET_DATA_NOT_VERIFIED"
    manifest["pnl_eligible"]=False
    (ROOT/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
    (ROOT/"network.json").write_text(json.dumps(network_all,indent=2,ensure_ascii=False))
    report=["# Phase 51-1J TradingTick Browser Audit","",f"**Classification:** {manifest['classification']}","",
      f"- Audit timestamp: {manifest['created_utc']}",f"- Same-origin data responses stored for inspection: {len(files_seen)}",
      f"- Browser network events observed: {len(network_all)}",f"- Target date present in some selector option: {any_target_option}",
      f"- Intraday-like timestamp found in observed response body: {any_intraday_payload}","- **P&L eligible: NO** (browser access is not proof of full-chain/contract coverage).","","## Page results",""]
    for slug,pdata in manifest["pages"].items():
      report += [f"### {slug}",f"- URL: {pdata.get('url')}",f"- Navigation status: {pdata.get('navigation_status')}",
        f"- Error: {pdata.get('error')}",f"- Select controls: {len(pdata.get('initial_selects',[]))}",
        f"- Browser requests/responses recorded: {pdata.get('request_count')}",""]
      for target,scan in pdata.get("selectors_by_target",{}).items():
        hits=[x for x in scan.get("target_option_scan",[]) if x.get("contains_target")]
        report.append(f"- {target}: attempted selections={len(scan.get('attempts',[]))}; controls containing this date={len(hits)}")
      report.append("")
    report += ["## Data-response manifest","","See manifest.json, network.json, and responses/ for response metadata and small public JSON/CSV response copies. Only responses served by ordinary browser requests are represented. No authenticated or protected route was accessed."]
    (ROOT/"REPORT.md").write_text("\n".join(report)+"\n")
    await browser.close()

asyncio.run(main())
