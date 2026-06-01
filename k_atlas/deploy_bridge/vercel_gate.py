import shutil
import subprocess

def inspect_vercel_readiness():
    cli = shutil.which("vercel")

    if not cli:
        npx = shutil.which("npx")
        if not npx:
            return {
                "status": "VERCEL_CLI_MISSING",
                "can_attempt_deploy": False,
                "cli_path": "",
                "message": "Vercel CLI nao encontrado. Instale com npm i -g vercel ou use npx vercel.",
            }

        return {
            "status": "VERCEL_CLI_MISSING",
            "can_attempt_deploy": False,
            "cli_path": "",
            "npx_path": npx,
            "message": "Vercel CLI direto nao encontrado. O deploy podera usar npx vercel em etapa assistida.",
        }

    try:
        proc = subprocess.run(
            [cli, "whoami"],
            capture_output=True,
            text=True,
            shell=False,
            timeout=20,
        )
    except FileNotFoundError:
        return {
            "status": "VERCEL_CLI_MISSING",
            "can_attempt_deploy": False,
            "cli_path": str(cli),
            "message": "Executavel Vercel nao abriu no Windows.",
        }
    except Exception as exc:
        return {
            "status": "VERCEL_LOGIN_REQUIRED",
            "can_attempt_deploy": False,
            "cli_path": str(cli),
            "message": str(exc),
        }

    logged = proc.returncode == 0

    return {
        "status": "VERCEL_READY" if logged else "VERCEL_LOGIN_REQUIRED",
        "can_attempt_deploy": logged,
        "cli_path": str(cli),
        "whoami": proc.stdout.strip() if logged else "",
        "message": "" if logged else "Execute vercel login antes do deploy real.",
    }
