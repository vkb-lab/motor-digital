import subprocess
from datetime import datetime


class AutoExecutor:

    def __init__(self):
        self.product_file = "k_atlas/products/data/product_20260527_174445.json"

    def log(self, message):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] {message}")

    def safe_print(self, text):
        if not text:
            return

        clean = (
            text
            .replace("\ufffd", "")
            .replace("🔥", "")
            .replace("ção", "cao")
            .replace("ções", "coes")
            .replace("ã", "a")
            .replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
            .replace("ç", "c")
        )

        print(clean)

    def run(self, command):
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        self.safe_print(result.stdout)
        self.safe_print(result.stderr)

    def execute(self):
        self.log("Executando agente: sales_orchestrator")
        self.run([
            "python",
            "-m",
            "k_atlas.products.sales_orchestrator",
            "--product",
            self.product_file,
            "--message",
            "Cliente urgente de piscina precisa resolver hoje"
        ])

        self.log("Executando agente: instagram_content_pack")
        self.run([
            "python",
            "-m",
            "k_atlas.agents.instagram_content_pack",
            "--file",
            self.product_file
        ])


if __name__ == "__main__":
    AutoExecutor().execute()
