"""Visit a Blackboard Ultra course with the saved auth state and log every
XHR/fetch the UI makes. Writes the results to tools/bb_traffic.json."""
from __future__ import annotations
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from uni.config import BLACKBOARD_STATE, BLACKBOARD_HOST


def main(course_id: str, out_path: str = "tools/bb_traffic.json", wait_s: int = 18) -> None:
    calls: list[dict] = []
    url = f"{BLACKBOARD_HOST}/ultra/courses/{course_id}/outline"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(storage_state=str(BLACKBOARD_STATE))
        page = ctx.new_page()

        def on_request(req):
            if "/learn/api/" in req.url or "/webapps/" in req.url:
                calls.append({
                    "method": req.method,
                    "url": req.url,
                    "type": req.resource_type,
                })

        page.on("request", on_request)
        print(f"Visiting {url} ...")
        page.goto(url, wait_until="networkidle", timeout=45000)
        page.wait_for_timeout(wait_s * 1000)
        browser.close()

    Path(out_path).write_text(json.dumps(calls, indent=2))
    print(f"Captured {len(calls)} API calls -> {out_path}")

    # Show unique endpoint patterns
    import re, collections
    patterns = collections.Counter()
    for c in calls:
        u = re.sub(r"/_\d+_\d+", "/{id}", c["url"].split("?")[0])
        u = re.sub(r"\d+", "{n}", u)
        patterns[(c["method"], u)] += 1
    print("\nUnique endpoint patterns:")
    for (m, u), n in patterns.most_common():
        print(f"  {n:3d}  {m}  {u}")


if __name__ == "__main__":
    course = sys.argv[1] if len(sys.argv) > 1 else "_46862_1"
    main(course)
