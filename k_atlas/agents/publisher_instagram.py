from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime

PROFILE_DIR = Path.cwd() / "k_atlas" / "browser" / "instagram_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)


def open_instagram_creator():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            slow_mo=250
        )

        page = context.new_page()
        print("[INFO] Abrindo Instagram...")
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")

        input("Depois de confirmar que está logado, pressione ENTER...")

        print("[INFO] Tentando abrir criação de postagem...")

        selectors = [
            "text=Criar",
            "text=Create",
            "svg[aria-label='Nova publicação']",
            "svg[aria-label='New post']",
            "a[href='/create/select/']",
            "div[role='button']:has-text('Criar')",
            "div[role='button']:has-text('Create')"
        ]

        opened = False

        for selector in selectors:
            try:
                page.locator(selector).first.click(timeout=3000)
                opened = True
                print(f"[OK] Clicou usando seletor: {selector}")
                break
            except Exception:
                pass

        if not opened:
            print("[AVISO] Não encontrei o botão automaticamente.")
            print("[AÇÃO MANUAL] Clique no botão + ou Criar no Instagram.")
            input("Depois que abrir a tela de criação, pressione ENTER...")

        screenshot_dir = Path.cwd() / "k_atlas" / "browser" / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        shot = screenshot_dir / f"instagram_creator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        page.screenshot(path=str(shot), full_page=True)

        print(f"[OK] Screenshot salvo em: {shot}")
        print("[OK] Instagram Creator validado.")

        input("Pressione ENTER para fechar...")
        context.close()


if __name__ == "__main__":
    open_instagram_creator()