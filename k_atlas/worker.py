import time
from k_atlas.services.supabase_service import (
    get_pending_tasks,
    save_report,
    update_task_status,
)

def run_worker(interval=10):
    print("🧠 K-Atlas Worker iniciado.")
    print("Lendo tarefas pendentes no Supabase...")

    while True:
        try:
            response = get_pending_tasks()
            tasks = response.data or []

            if not tasks:
                print("Sem tarefas pendentes.")

            for task in tasks:
                task_id = task["id"]
                title = task.get("title", "Sem título")
                instruction = task.get("instruction", "")

                print(f"Executando tarefa: {title}")

                update_task_status(task_id, "running")

                result = f"Tarefa executada com sucesso.\n\n{instruction}"

                save_report(
                    title=f"Resultado - {title}",
                    content=result,
                )

                update_task_status(
                    task_id,
                    "done",
                    result,
                )

                print(f"Tarefa concluída: {task_id}")

        except KeyboardInterrupt:
            print("Worker encerrado pelo usuário.")
            break

        except Exception as e:
            print(f"Erro no worker: {e}")

        time.sleep(interval)

if __name__ == "__main__":
    run_worker()