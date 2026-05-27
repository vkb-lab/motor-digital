import sys
from pathlib import Path
from datetime import datetime

from k_atlas.core.safe_executor import execute_plan


def main():
    if len(sys.argv) < 2:
        print("K-Atlas Local")
        print("")
        print("Uso:")
        print('  python -m k_atlas.run "seu pedido aqui"')
        print("")
        print("Exemplos:")
        print('  python -m k_atlas.run "crie uma landing page para Parada Atlântida vender chopp grátis"')
        print('  python -m k_atlas.run "analise minha área de trabalho"')
        print('  python -m k_atlas.run "abra o gmail"')
        return

    command = " ".join(sys.argv[1:]).strip()

    print("")
    print("🧭 K-Atlas recebeu:")
    print(command)
    print("")

    plan, results = execute_plan(command, auto_confirm=False)

    print(plan.to_markdown())
    print("")
    print("RESULTADOS:")
    for item in results:
        print(f"- {item}")

    summary_dir = Path.cwd() / "k_atlas" / "reports"
    summary_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = summary_dir / f"run_summary_{stamp}.md"

    content = []
    content.append("# Execução K-Atlas")
    content.append("")
    content.append(f"Data: {datetime.now().isoformat()}")
    content.append("")
    content.append("## Pedido")
    content.append(command)
    content.append("")
    content.append("## Plano")
    content.append(plan.to_markdown())
    content.append("")
    content.append("## Resultados")
    for item in results:
        content.append(f"- {item}")

    summary_file.write_text("\n".join(content), encoding="utf-8")

    print("")
    print(f"Resumo salvo em: {summary_file}")


if __name__ == "__main__":
    main()
