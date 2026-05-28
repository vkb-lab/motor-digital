import json
from datetime import datetime
from pathlib import Path


class ActionRouter:

    def __init__(self):

        self.base_dir = Path("k_atlas")

        self.routes = {
            "piscina": [
                "customer_profiler",
                "sales_orchestrator",
                "instagram_content_pack"
            ],

            "instagram": [
                "publisher_instagram"
            ],

            "campanha": [
                "instagram_content_pack",
                "sales_orchestrator"
            ],

            "cliente": [
                "customer_profiler"
            ]
        }

    def log(self, message):

        now = datetime.now().strftime("%H:%M:%S")

        print(f"[{now}] {message}")

    def detect_routes(self, command):

        command = command.lower()

        activated = []

        for keyword, agents in self.routes.items():

            if keyword in command:

                for agent in agents:

                    if agent not in activated:
                        activated.append(agent)

        return activated

    def create_report(self, command, agents):

        report = {
            "created_at": datetime.now().isoformat(),
            "command": command,
            "agents_selected": agents
        }

        reports_dir = self.base_dir / "reports"

        reports_dir.mkdir(parents=True, exist_ok=True)

        filename = reports_dir / f"router_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log(f"Relatorio salvo: {filename}")

    def execute(self, command):

        self.log("ANALISANDO COMANDO")

        agents = self.detect_routes(command)

        if not agents:

            print("\n[K-ATLAS]: Nenhum agente encontrado.")
            return

        print("\n[K-ATLAS]: Agentes ativados:\n")

        for agent in agents:

            print(f" - {agent}")

        self.create_report(command, agents)


if __name__ == "__main__":

    router = ActionRouter()

    command = input("Comando: ")

    router.execute(command)