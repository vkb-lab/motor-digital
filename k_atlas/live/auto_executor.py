import subprocess
from datetime import datetime


class AutoExecutor:

    def __init__(self):

        self.agents_map = {
            "customer_profiler": [
                "python",
                "-m",
                "k_atlas.products.customer_profiler",
                "--message"
            ],

            "instagram_content_pack": [
                "python",
                "-m",
                "k_atlas.agents.instagram_content_pack",
                "--file"
            ],

            "sales_orchestrator": [
                "python",
                "-m",
                "k_atlas.products.sales_orchestrator",
                "--product"
            ],

            "publisher_instagram": [
                "python",
                "-m",
                "k_atlas.agents.publisher_instagram"
            ]
        }

    def log(self, message):

        now = datetime.now().strftime("%H:%M:%S")

        print(f"[{now}] {message}")

    def run_agent(self, agent_name, value=None):

        if agent_name not in self.agents_map:

            self.log(f"Agente nao encontrado: {agent_name}")
            return

        command = self.agents_map[agent_name].copy()

        if value:
            command.append(value)

        self.log(f"Executando agente: {agent_name}")

        try:

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            print(result.stdout)

        except Exception as e:

            self.log(f"Erro no agente {agent_name}: {e}")


if __name__ == "__main__":

    executor = AutoExecutor()

    product_file = "k_atlas/products/data/product_20260527_174445.json"

    executor.run_agent(
        "sales_orchestrator",
        product_file
    )

    executor.run_agent(
        "instagram_content_pack",
        product_file
    )