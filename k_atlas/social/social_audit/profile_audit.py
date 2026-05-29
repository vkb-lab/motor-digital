from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from .live_status import SocialAuditLiveStatus


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_excerpt(text: str, limit: int = 2000) -> str:
    return " ".join(text.split())[:limit]


def try_click_by_text(page, text: str) -> None:
    try:
        locator = page.get_by_text(text, exact=False).first
        if locator.count() > 0:
            locator.click(timeout=2000)
            page.wait_for_timeout(800)
    except Exception:
        pass


def take_step_screenshot(page, audit_dir: Path, step: str) -> str:
    path = audit_dir / f"{step}.png"
    try:
        page.screenshot(path=str(path), full_page=True)
    except Exception:
        return ""
    return str(path).replace("\\", "/")


def run_profile_audit(
    url: str,
    output_root: str = "reports/social_audit",
    headed: bool = True,
    slow_mo: int = 500,
    observe_seconds: int = 5,
) -> dict:
    run_id = str(uuid4())
    stamp = now_stamp()
    audit_dir = Path(output_root) / stamp
    audit_dir.mkdir(parents=True, exist_ok=True)

    live = SocialAuditLiveStatus()

    screenshot_path = audit_dir / "page.png"
    report_path = audit_dir / "report.json"

    result = {
        "ok": False,
        "run_id": run_id,
        "target_url": url,
        "final_url": "",
        "title": "",
        "meta_title": "",
        "meta_description": "",
        "h1": [],
        "body_excerpt": "",
        "screenshots": [],
        "screenshot_path": str(screenshot_path).replace("\\", "/"),
        "report_path": str(report_path).replace("\\", "/"),
        "audit_dir": str(audit_dir).replace("\\", "/"),
        "notes": [],
    }

    live.update(run_id, "starting", "init", "Preparando auditoria visual.", {"target_url": url})

    with sync_playwright() as p:
        live.update(run_id, "running", "browser_launch", "Abrindo navegador visual local.")

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
            live.update(run_id, "running", "navigate", "Acessando URL alvo.", {"url": url})
            page.goto(url, wait_until="domcontentloaded", timeout=90000)
            page.wait_for_timeout(3000)

            shot = take_step_screenshot(page, audit_dir, "01_loaded")
            if shot:
                result["screenshots"].append(shot)
                live.update(run_id, "running", "screenshot_loaded", "Screenshot inicial capturado.", {"screenshot": shot})

            live.update(run_id, "running", "cookie_modals", "Tentando fechar modais comuns sem forcar login.")
            for text in [
                "Permitir todos os cookies",
                "Allow all cookies",
                "Agora não",
                "Not now",
                "Fechar",
                "Close",
            ]:
                try_click_by_text(page, text)

            page.wait_for_timeout(1500)

            shot = take_step_screenshot(page, audit_dir, "02_after_modals")
            if shot:
                result["screenshots"].append(shot)
                live.update(run_id, "running", "screenshot_after_modals", "Screenshot apos modais capturado.", {"screenshot": shot})

            live.update(run_id, "running", "extract_metadata", "Extraindo metadados e textos visiveis.")

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

            live.update(
                run_id,
                "running",
                "observe",
                f"Observando visualmente por {observe_seconds} segundos.",
                {"observe_seconds": observe_seconds},
            )
            page.wait_for_timeout(max(1, observe_seconds) * 1000)

            page.screenshot(path=str(screenshot_path), full_page=True)
            result["screenshots"].append(str(screenshot_path).replace("\\", "/"))

            result["ok"] = True
            result["notes"].append("audit_completed")

            live.update(
                run_id,
                "completed",
                "finished",
                "Auditoria concluida. Relatorio e screenshots salvos.",
                {
                    "report_path": str(report_path).replace("\\", "/"),
                    "screenshot_path": str(screenshot_path).replace("\\", "/"),
                    "audit_dir": str(audit_dir).replace("\\", "/"),
                },
            )

        except PlaywrightTimeoutError:
            try:
                page.screenshot(path=str(screenshot_path), full_page=True)
            except Exception:
                pass
            result["notes"].append("timeout_during_navigation")
            live.update(run_id, "failed", "timeout", "Timeout durante navegacao.", {"url": url})
        except Exception as exc:
            try:
                page.screenshot(path=str(screenshot_path), full_page=True)
            except Exception:
                pass
            result["notes"].append(f"error:{type(exc).__name__}:{exc}")
            live.update(run_id, "failed", "error", f"Erro durante auditoria: {type(exc).__name__}", {"error": str(exc)})
        finally:
            live.update(run_id, "closing", "browser_close", "Fechando navegador visual local.")
            browser.close()

    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--output-root", default="reports/social_audit")
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--slow-mo", type=int, default=500)
    parser.add_argument("--observe-seconds", type=int, default=5)
    args = parser.parse_args()

    result = run_profile_audit(
        url=args.url,
        output_root=args.output_root,
        headed=args.headed,
        slow_mo=args.slow_mo,
        observe_seconds=args.observe_seconds,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()