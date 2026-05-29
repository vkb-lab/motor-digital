# K-Atlas Control Plane

Checkpoint 26.

O Control Plane e o cerebro operacional central do K-Atlas OS.

## Objetivo

Transformar modulos isolados em um sistema operacional governado.

Fluxo:

objetivo -> tarefa -> agente -> permissao -> aprovacao -> execucao segura -> evento -> relatorio

## Componentes

- agent_registry.py: registra agentes, dominios e permissoes.
- autonomy_policy.py: decide allow, deny ou require_approval.
- event_bus.py: log central de eventos.
- supervisor_queue.py: fila central de aprovacao humana.
- task_router.py: roteia objetivos para agentes.
- system_state.py: estado operacional central.
- health_check.py: validacao basica do Control Plane.
- smoke_test_control_plane.py: teste operacional.

## Regras

- Nenhuma acao critica executa sem politica.
- Nenhum segredo pode ser salvo em texto puro.
- Publicacao oficial continua bloqueada.
- Mass messaging continua bloqueado.
- Browser automation continua bloqueado.
- Toda tarefa cria evento.
- Toda acao supervisionada entra na fila do supervisor.

## Proximo passo

Expor o Control Plane no cockpit Streamlit e conectar:
- K-Social
- SaaS Factory
- Creative Media Gateway
- AutoReporter
- Deploy pipeline