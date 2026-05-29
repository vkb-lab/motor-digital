from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_excerpt(text: str, limit: int = 2000) -> str:
    return " ".join(text.split())[:limit]


def try_click_by_text(page, text: str) -> None:
    try:
        locator = page.get_by_text(text, exact=False).first
        if locator.count() > 0:
            locator.click(timeout=2000)
            page.wait_for_timeout(1000)
    except Exception:
        pass


def run_profile_audit(
    url: str,
    output_root: str = "reports/social_audit",
    headed: bool = True,
    slow_mo: int = 500,
) -> dict:
    stamp = now_stamp()
    audit_dir = Path(output_root) / stamp
    audit_dir.mkdir(parents=True, exist_ok=True)

    screenshot_path = audit_dir / "page.png"
    report_path = audit_dir / "report.json"

    result = {
        "ok": False,
        "target_url": url,
        "final_url": "",
        "title": "",
        "meta_title": "",
        "meta_description": "",
        "h1": [],
        "body_excerpt": "",
        "screenshot_path": str(screenshot_path),
        "report_path": str(report_path),
        "audit_dir": str(audit_dir),
        "notes": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=not headed,
            slow_mo=slow_mo,
        )

        context = browser.new_context(
            viewport={"width": 1440, "height": 2200},
            locale="pt-BR",
        )

        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=90000)
            page.wait_for_timeout(5000)

            for text in [
                "Permitir todos os cookies",
                "Allow all cookies",
                "Agora não",
                "Not now",
                "Fechar",
                "Close",
            ]:
                try_click_by_text(page, text)

            page.wait_for_timeout(2500)

            result["final_url"] = page.url
            result["title"] = page.title()

            try:
                result["meta_title"] = page.locator('meta[property="og:title"]').get_attribute("content", timeout=3000) or ""
            except Exception:
                result["meta_title"] = ""

            try:
                result["meta_description"] = page.locator('meta[property="og:description"]').get_attribute("content", timeout=3000) or ""
            except Exception:
                result["meta_description"] = ""

            try:
                result["h1"] = page.locator("h1").all_inner_texts()
            except Exception:
                result["h1"] = []

            try:
                body_text = page.locator("body").inner_text(timeout=5000)
                result["body_excerpt"] = safe_excerpt(body_text)
            except Exception:
                result["body_excerpt"] = ""

            page.screenshot(path=str(screenshot_path), full_page=True)
            result["ok"] = True
            result["notes"].append("audit_completed")

        except PlaywrightTimeoutError:
            page.screenshot(path=str(screenshot_path), full_page=True)
            result["notes"].append("timeout_during_navigation")
        except Exception as exc:
            try:
                page.screenshot(path=str(screenshot_path), full_page=True)
            except Exception:
                pass
            result["notes"].append(f"error:{type(exc).__name__}:{exc}")
        finally:
            browser.close()

    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--output-root", default="reports/social_audit")
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--slow-mo", type=int, default=500)
    args = parser.parse_args()

    result = run_profile_audit(
        url=args.url,
        output_root=args.output_root,
        headed=args.headed,
        slow_mo=args.slow_mo,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()