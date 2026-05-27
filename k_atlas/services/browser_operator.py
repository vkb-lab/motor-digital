from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright


BASE = Path.cwd()
SCREENSHOTS = BASE / "k_atlas" / "browser" / "screenshots"
LOGS = BASE / "k_atlas" / "browser" / "logs"

SCREENSHOTS.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)


def log(message: str):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    print(line)

    with (LOGS / "browser_operator.log").open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def open_google_and_search(query: str):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = SCREENSHOTS / f"google_search_{stamp}.png"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=250
        )

        page = browser.new_page()
        log("Abrindo Google.")
        page.goto("https://www.google.com", wait_until="domcontentloaded")

        try:
            page.get_by_role("button", name="Accept all").click(timeout=3000)
        except Exception:
            pass

        try:
            page.get_by_role("button", name="Aceitar tudo").click(timeout=3000)
        except Exception:
            pass

        log(f"Pesquisando: {query}")
        page.fill("textarea[name='q'], input[name='q']", query)
        page.keyboard.press("Enter")

        page.wait_for_load_state("networkidle", timeout=15000)
        page.screenshot(path=str(screenshot_path), full_page=True)

        log(f"Screenshot salvo em: {screenshot_path}")

        input("Pressione ENTER para fechar o navegador...")
        browser.close()

    return screenshot_path


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or "K-Atlas K-Work"
    open_google_and_search(query)