import json
import shutil
from pathlib import Path
from datetime import datetime

from k_atlas.core.project_builder import create_basic_web_files
from k_atlas.core.landing_evolver import find_latest_landing, evolve_landing


BASE = Path.cwd()
PENDING = BASE / "k_atlas" / "execution" / "pending"
DONE = BASE / "k_atlas" / "execution" / "done"
LOGS = BASE / "k_atlas" / "execution" / "logs"
WORKSPACE = BASE / "k_atlas" / "workspace"

DONE.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)


def log(message: str):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    print(line)
    with (LOGS / "approval_execution.log").open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def find_latest_pending():
    files = sorted(
        PENDING.glob("approval_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    return files[0] if files else None


def find_latest_project_folder():
    folders = [p for p in WORKSPACE.iterdir() if p.is_dir()]
    if not folders:
        return None
    return sorted(folders, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def move_done(approval_file: Path):
    done_file = DONE / approval_file.name
    shutil.move(str(approval_file), str(done_file))
    log(f"Aprovação movida para: {done_file}")


def main():
    approval_file = find_latest_pending()

    if not approval_file:
        log("Nenhuma aprovação pendente encontrada.")
        return

    data = json.loads(approval_file.read_text(encoding="utf-8-sig"))
    step = data.get("step", {})
    action = step.get("action")

    log(f"Aprovação encontrada: {approval_file}")
    log(f"Ação solicitada: {action}")

    if action == "create_basic_web_files":
        project_path = find_latest_project_folder()

        if not project_path:
            log("Nenhuma pasta de projeto encontrada no workspace.")
            return

        original_command = data.get("original_command", "")

        try:
            files = create_basic_web_files(project_path, original_command)
        except TypeError:
            files = create_basic_web_files(project_path)

        log(f"Arquivos web criados em: {project_path}")
        for f in files:
            log(f"Arquivo criado: {f}")

        move_done(approval_file)
        return

    if action == "evolve_latest_landing":
        project_path = find_latest_landing()

        if not project_path:
            log("Nenhuma landing encontrada para evoluir.")
            return

        files = evolve_landing(project_path)

        log(f"Landing evoluída em: {project_path}")
        for f in files:
            log(f"Arquivo atualizado: {f}")

        move_done(approval_file)
        return

    log(f"Ação ainda não suportada pelo approve_next.py: {action}")


if __name__ == "__main__":
    main()
