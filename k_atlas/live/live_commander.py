import json
import subprocess
from datetime import datetime
from pathlib import Path


class LiveCommander:

    def __init__(self):
        self.base_dir = Path("k_atlas")
        self.memory_dir = self.base_dir / "memory"
        self.products_dir = self.base_dir / "products" / "data"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.products_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] {message}")

    def save_memory(self, command, response):
        memory = {
            "created_at": datetime.now().isoformat(),
            "command": command,
            "response": response
        }

        filename = self.memory_dir / f"live_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)

        self.log(f"Memoria salva: {filename}")

    def run_profiler(self, command):
        profile_file = self.products_dir / "live_profile.json"

        result = subprocess.run(
            [
                "python",
                "-m",
                "k_atlas.products.customer_profiler",
                "--message",
                command
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        output = result.stdout or "{}"

        profile_file.write_text(output, encoding="utf-8")

        return "Cliente de piscina identificado e perfilado."

    def execute_command(self, command):
        normalized = command.lower()

        if "piscina" in normalized:
            response = self.run_profiler(command)
            self.save_memory(command, response)
            return response

        if "instagram" in normalized:
            response = "Instagram detectado. Modulo social pronto para acionamento."
            self.save_memory(command, response)
            return response

        response = "Comando entendido, mas ainda sem acao programada."
        self.save_memory(command, response)
        return response

    def run(self):
        self.log("LIVE COMMANDER INICIADO")

        while True:
            try:
                command = input("\nK-Atlas > ")

                if command.lower() in ["sair", "exit", "quit"]:
                    self.log("Encerrando sistema.")
                    break

                response = self.execute_command(command)

                print(f"\n[K-ATLAS]: {response}")

            except KeyboardInterrupt:
                self.log("Sistema interrompido.")
                break

            except Exception as e:
                self.log(f"Erro: {e}")


if __name__ == "__main__":
    app = LiveCommander()
    app.run()
