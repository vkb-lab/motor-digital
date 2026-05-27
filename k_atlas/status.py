from pathlib import Path
from datetime import datetime


BASE = Path.cwd()
K = BASE / "k_atlas"


def count_files(path: Path, pattern="*"):
    if not path.exists():
        return 0
    return len(list(path.glob(pattern)))


def main():
    reports = K / "reports"
    plans = K / "plans"
    workspace = K / "workspace"
    pending = K / "execution" / "pending"
    done = K / "execution" / "done"

    print("")
    print("🧭 STATUS K-ATLAS LOCAL")
    print("")

    print(f"Base: {BASE}")
    print(f"K-Atlas: {K}")
    print("")

    print("📁 Estrutura")
    print(f"- Projetos no workspace: {count_files(workspace)} itens diretos")
    print(f"- Planos criados: {count_files(plans, '*.md')}")
    print(f"- Relatórios criados: {count_files(reports, '*.md')}")
    print(f"- Aprovações pendentes: {count_files(pending, '*.json')}")
    print(f"- Aprovações concluídas: {count_files(done, '*.json')}")
    print("")

    print("✅ Comandos disponíveis")
    print('- .\\scripts\\atlas.ps1 "seu pedido"')
    print("- .\\scripts\\aprovar.ps1")
    print("- python -m k_atlas.run \"seu pedido\"")
    print("- python -m k_atlas.scripts.approve_next")
    print("")

    if pending.exists():
        pending_files = list(pending.glob("*.json"))
        if pending_files:
            print("⚠️ Aprovações pendentes:")
            for f in pending_files:
                print(f"- {f}")
            print("")
            print("Para aprovar a próxima:")
            print(".\\scripts\\aprovar.ps1")
            print("")

    print("Próximo passo sugerido:")
    print("Criar painel cowork com campo único, lousa e botão de aprovação.")
    print("")


if __name__ == "__main__":
    main()
