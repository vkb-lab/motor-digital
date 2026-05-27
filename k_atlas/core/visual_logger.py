from datetime import datetime
from pathlib import Path
import traceback


BASE_DIR = Path.cwd()
LOG_DIR = BASE_DIR / "k_atlas" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

VISUAL_LOG = LOG_DIR / "visual_timeline.log"
DEBUG_LOG = LOG_DIR / "debug.log"


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_visual(message: str):
    clean = str(message).replace("\n", " ").strip()
    line = f"[{_now()}] {clean}"
    with VISUAL_LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    return line


def log_debug(error):
    with DEBUG_LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n[{_now()}] DEBUG ERROR\n")
        f.write(str(error) + "\n")
        f.write(traceback.format_exc())
        f.write("\n")


def get_timeline(limit: int = 30):
    if not VISUAL_LOG.exists():
        return []
    lines = VISUAL_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()
    return lines[-limit:]


def human_error(error) -> str:
    text = str(error)
    if "DevToolsActivePort" in text:
        return "O Chrome automatizado falhou ao iniciar. O navegador pode já estar aberto ou o ChromeDriver travou."
    if "FileExistsError" in text or "already exists" in text:
        return "Existe um arquivo de backup antigo. A ação precisa usar backup com data/hora."
    if "SyntaxError" in text:
        return "Um arquivo Python ficou com sintaxe inválida. Provável código gerado com formatação errada."
    if "dotenv could not parse" in text:
        return "O arquivo .env tem uma linha mal formatada. Precisamos revisar a linha indicada."
    return "Ocorreu um erro técnico. Detalhes foram salvos no debug.log."
