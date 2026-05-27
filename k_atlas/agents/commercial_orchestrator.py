import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


class CommercialOrchestrator:

    def __init__(self):
        self.base_dir = Path("k_atlas")
        self.products_dir = self.base_dir / "products" / "data"
        self.content_dir = self.base_dir / "content_packs"
        self.memory_dir = self.base_dir / "memory"

        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] {message}")

    def execute_command(self, command):
        self.log(f"Executando: {command}")

result = subprocess.run(
    command,
    shell=True,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"
)

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(result.stderr)

        return result

    def generate_customer_profile(self, message):

        output_file = self.products_dir / "customer_profile.json"

        command = (
            f'python -m k_atlas.products.customer_profiler '
            f'--message "{message}" > "{output_file}"'
        )

        self.execute_command(command)

        return output_file

    def generate_instagram_pack(self, product_file):

        command = (
            f'python -m k_atlas.agents.instagram_content_pack '
            f'--file "{product_file}"'
        )

        self.execute_command(command)

    def save_memory(self, data):

        filename = (
            self.memory_dir /
            f"memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.log(f"Memória salva em: {filename}")

    def execute(self, product_file, customer_message):

        self.log("INICIANDO ORQUESTRAÇÃO COMERCIAL")

        profile_file = self.generate_customer_profile(
            customer_message
        )

        self.generate_instagram_pack(product_file)

        memory = {
            "created_at": datetime.now().isoformat(),
            "product_file": str(product_file),
            "customer_message": customer_message,
            "profile_file": str(profile_file),
            "status": "processed"
        }

        self.save_memory(memory)

        self.log("PROCESSO FINALIZADO")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--product",
        required=True
    )

    parser.add_argument(
        "--message",
        required=True
    )

    args = parser.parse_args()

    app = CommercialOrchestrator()

    app.execute(
        args.product,
        args.message
    )