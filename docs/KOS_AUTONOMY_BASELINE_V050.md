# K-OS Autonomy Baseline v0.50.0

## Status

Baseline operacional local certificada.

- Branch: kos/fase-18-render-public-asset-bridge
- Commit base: 53e85ae
- Criado em: 2026-06-16T14:56:07.3837402-03:00
- Runtime local: ativo via Startup Folder
- IA paga: bloqueada
- Instagram real: bloqueado
- Codex automatico: bloqueado
- Publicacao externa: bloqueada
- Git status no momento da certificacao:

```text
workspace limpo
```

## Comandos principais

### Status geral

```powershell
powershell -ExecutionPolicy Bypass -File scripts\kos_runtime_control.ps1 -Action status
```

### Health check

```powershell
powershell -ExecutionPolicy Bypass -File scripts\kos_runtime_control.ps1 -Action health
```

### Briefing operacional

```powershell
powershell -ExecutionPolicy Bypass -File scripts\kos_runtime_control.ps1 -Action briefing
```

### Evidence ledger

```powershell
powershell -ExecutionPolicy Bypass -File scripts\kos_runtime_control.ps1 -Action evidence
```

### Iniciar runtime local

```powershell
powershell -ExecutionPolicy Bypass -File scripts\kos_runtime_control.ps1 -Action start
```

Confirmacao exigida:

```text
YES_START_KOS_RUNTIME_LOCAL
```

### Parar runtime local

```powershell
powershell -ExecutionPolicy Bypass -File scripts\kos_runtime_control.ps1 -Action stop
```

Confirmacao exigida:

```text
YES_STOP_KOS_RUNTIME_LOCAL
```

### Reiniciar runtime local

```powershell
powershell -ExecutionPolicy Bypass -File scripts\kos_runtime_control.ps1 -Action restart
```

Confirmacao exigida:

```text
YES_RESTART_KOS_RUNTIME_LOCAL
```

### Remover inicializacao no login

```powershell
powershell -ExecutionPolicy Bypass -File scripts\unregister_kos_autonomy_startup_folder.ps1
```

## Garantias da baseline

- Nao publica Instagram.
- Nao chama IA paga.
- Nao executa Codex automaticamente.
- Nao acessa segredos.
- Nao faz commit automatico.
- Nao faz push automatico.
- Toda execucao relevante gera log local.
- O operador humano continua no controle.

## Proxima expansao recomendada

Fase 51 - Product Factory Mission Layer.

Objetivo: transformar ideias em missoes estruturadas para gerar apps, SaaS, campanhas e automacoes dentro da governanca atual.
