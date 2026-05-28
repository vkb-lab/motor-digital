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

    def run_subprocess(self, args):
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

    def run_profiler(self, command):
        profile_file = self.products_dir / "live_profile.json"

        result = self.run_subprocess([
            "python",
            "-m",
            "k_atlas.products.customer_profiler",
            "--message",
            command
        ])

        output = result.stdout or "{}"
        profile_file.write_text(output, encoding="utf-8")

        return "Cliente de piscina identificado e perfilado."

    def run_router(self, command):
        result = self.run_subprocess([
            "python",
            "-m",
            "k_atlas.live.action_router"
        ])

        return result.stdout or "Router acionado."

    def run_auto_executor(self):
        result = self.run_subprocess([
            "python",
            "-m",
            "k_atlas.live.auto_executor"
        ])

        return result.stdout or "Auto executor acionado."

    def execute_command(self, command):
        normalized = command.lower()
        responses = []

        if "piscina" in normalized or "cliente" in normalized:
            responses.append(self.run_profiler(command))

        if "instagram" in normalized or "conteudo" in normalized or "conteúdo" in normalized:
            responses.append("Instagram/conteudo detectado. Acionando roteador e executor.")
            responses.append(self.run_auto_executor())

        if not responses:
            responses.append("Comando entendido, mas ainda sem acao programada.")

        final_response = "\n".join(responses)
        self.save_memory(command, final_response)
        return final_response

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