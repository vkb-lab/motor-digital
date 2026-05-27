import time
from k_atlas.services.supabase_service import get_pending_tasks, save_report
from k_atlas.core.safe_executor import execute_plan


def run_worker(interval=10):
    print("🧠 K-Atlas Worker iniciado.")
    print("Lendo tarefas pendentes no Supabase...")

    while True:
        try:
            response = get_pending_tasks()
            tasks = response.data or []

            if not tasks:
                print("Sem tarefas pendentes.")
            else:
                for task in tasks:
                    task_id = task.get("id")
                    title = task.get("title") or "Tarefa Supabase"
                    instruction = task.get("instruction") or title

                    print(f"Executando tarefa: {title}")

                    plan, results = execute_plan(instruction, auto_confirm=False)

                    content = []
                    content.append(f"# Resultado da tarefa {task_id}")
                    content.append("")
                    content.append("## Pedido")
                    content.append(instruction)
                    content.append("")
                    content.append("## Plano")
                    content.append(plan.to_markdown())
                    content.append("")
                    content.append("## Resultados")
                    for r in results:
                        content.append(f"- {r}")

                    save_report(
                        title=f"Resultado Worker - {title}",
                        content="\n".join(content)
                    )

                    print(f"Tarefa processada: {task_id}")
                    print("Resultado salvo em k_reports.")

        except KeyboardInterrupt:
            print("Worker encerrado pelo usuário.")
            break

        except Exception as e:
            print(f"Erro no worker: {e}")

        time.sleep(interval)


if __name__ == "__main__":
    run_worker()