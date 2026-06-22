# K-OS AI Tools Phase 1 Readiness Audit

Status: auditoria de prontidao criada. Nenhuma instalacao executada.

## Politica
- Nenhuma dependencia instalada
- Nenhuma IA externa conectada
- Nenhuma API key usada
- Nenhum gasto executado

## codebase-memory-mcp
- Caminho: C:\Users\oi\Desktop\ai-tools\codebase-memory-mcp
- Commit: 53ebeb4 docs(security): coordinated-disclosure process + realistic reporting policy
- package.json: False
- pyproject.toml: False
- requirements.txt: False
- Cargo.toml: False
- go.mod: False
- Dockerfile: False

### Sinais de instalacao
**The fastest and most efficient code intelligence engine for AI coding agents.** Full-indexes an average repository in milliseconds, the Linux kernel (28M LOC, 75K files) in 3 minutes. Answers structural queries in under 1ms. Ships as a single static binary for macOS, Linux, and Windows — download, run `install`, done. | - **Plug and play** — single static binary for macOS (arm64/amd64), Linux (arm64/amd64), and Windows (amd64). No Docker, no runtime dependencies, no API keys. Download → `install` → restart agent → done. | - **158 languages** — vendored tree-sitter grammars compiled into the binary. Nothing to install, nothing that breaks. | - **11 agents, one command** — `install` auto-detects Claude Code, Codex CLI, Gemini CLI, Zed, OpenCode, Antigravity, Aider, KiloCode, VS Code, OpenClaw, and Kiro — configures MCP entries, instruction files, and pre-tool hooks for each. | - **Infrastructure-as-code indexing** — Dockerfiles, Kubernetes manifests, and Kustomize overlays indexed as graph nodes with cross-references. `Resource` nodes for K8s kinds, `Module` nodes for Kustomize overlays with `IMPORTS` edges to referenced resources. | **One-line install** (macOS / Linux): | curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash | curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash -s -- --ui | # 1. Download the installer | Invoke-WebRequest -Uri https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.ps1 -OutFile install.ps1 | notepad install.ps1 | .\install.ps1

### Sinais de execucao
# codebase-memory-mcp | [![GitHub Release](https://img.shields.io/github/v/release/DeusData/codebase-memory-mcp?style=flat&color=blue)](https://github.com/DeusData/codebase-memory-mcp/releases/latest) | [![CI](https://img.shields.io/github/actions/workflow/status/DeusData/codebase-memory-mcp/dry-run.yml?label=CI)](https://github.com/DeusData/codebase-memory-mcp/actions/workflows/dry-run.yml) | [![Tests](https://img.shields.io/badge/tests-5604_passing-brightgreen)](https://github.com/DeusData/codebase-memory-mcp) | [![Languages](https://img.shields.io/badge/languages-158-orange)](https://github.com/DeusData/codebase-memory-mcp) | [![Agents](https://img.shields.io/badge/agents-11-purple)](https://github.com/DeusData/codebase-memory-mcp) | [![Pure C](https://img.shields.io/badge/pure_C-zero_dependencies-blue)](https://github.com/DeusData/codebase-memory-mcp) | [![Platform](https://img.shields.io/badge/macOS_%7C_Linux_%7C_Windows-supported-lightgrey)](https://github.com/DeusData/codebase-memory-mcp/releases/latest) | [![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/DeusData/codebase-memory-mcp/badge)](https://scorecard.dev/viewer/?uri=github.com/DeusData/codebase-memory-mcp) | [![VirusTotal](https://img.shields.io/badge/VirusTotal-scanned_every_release-brightgreen?logo=virustotal)](https://github.com/DeusData/codebase-memory-mcp/releases/latest) | **The fastest and most efficient code intelligence engine for AI coding agents.** Full-indexes an average repository in milliseconds, the Linux kernel (28M LOC, 75K files) in 3 minutes. Answers structural queries in under 1ms. Ships as a single static binary for macOS, Linux, and Windows — download, run `install`, done. | High-quality parsing through [tree-sitter](https://tree-sitter.github.io/tree-sitter/) AST analysis across all 158 languages, enhanced with [**Hybrid LSP** semantic type resolution](#hybrid-lsp) for Python, TypeScript / JavaScript / JSX / TSX, PHP, C#, Go, C, C++, Java, Kotlin, and Rust — producing a persistent knowledge graph of functions, classes, call chains, HTTP routes, and cross-service links. 14 MCP tools. Zero dependencies. Plug and play across 11 coding agents.

## headroom
- Caminho: C:\Users\oi\Desktop\ai-tools\headroom
- Commit: 95b2333 chore: release main (#1274)
- package.json: False
- pyproject.toml: True
- requirements.txt: False
- Cargo.toml: True
- go.mod: False
- Dockerfile: True

### Sinais de instalacao
<a href="#get-started-60-seconds">Install</a> · | # 1 — Install | pip install "headroom-ai[all]"          # Python | npm install headroom-ai                 # Node / TypeScript | | OpenClaw     | ✅              | installs as ContextEngine plugin | | Any OpenAI-compatible client works via `headroom proxy`. MCP-native: `headroom mcp install`. | Platform support note: macOS auth reuse via Copilot CLI Keychain storage has been smoke-tested. Windows Credential Manager, Linux Secret Service / `secret-tool`, and Docker/CI token-injection paths are implemented or planned as auth-discovery paths, but still need real OS validation before they should be considered fully vetted. For Docker and CI, prefer passing an explicit `GITHUB_COPILOT_TOKEN` or `GITHUB_COPILOT_GITHUB_TOKEN` rather than relying on host keychain access. | | Your setup             | Hook in with                                                     | | | MCP clients            | `headroom mcp install`                                           | | `Setup` → `Pre-Start` → `Post-Start` → `Input Received` → `Input Cached` → `Input Routed` → `Input Compressed` → `Input Remembered` → `Pre-Send` → `Post-Send` → `Response Received` | ## Install | pip install "headroom-ai[all]"          # Python, everything

### Sinais de execucao
<p align="center"><strong>60–95% fewer tokens · library · proxy · MCP · 6 algorithms · local-first · reversible</strong></p> | <a href="#get-started-60-seconds">Install</a> · | - **Library** — `compress(messages)` in Python or TypeScript, inline in any app | - **Agent wrap** — `headroom wrap claude|codex|cursor|aider|copilot` in one command | - **MCP server** — `headroom_compress`, `headroom_retrieve`, `headroom_stats` for any MCP client | │  Headroom   (runs locally — your data stays here)  │ | │  Cross-agent memory  ·  headroom learn  ·  MCP     │ | ## Get started (60 seconds) | pip install "headroom-ai[all]"          # Python | npm install headroom-ai                 # Node / TypeScript | Granular extras: `[proxy]`, `[mcp]`, `[ml]`, `[code]`, `[memory]`, `[relevance]`, `[image]`, `[agno]`, `[langchain]`, `[evals]`, `[pytorch-mps]` (Apple-GPU memory-embedder offload — set `HEADROOM_EMBEDDER_RUNTIME=pytorch_mps`). Requires **Python 3.10+**. | **Accuracy preserved on standard benchmarks:**

## skills
- Caminho: C:\Users\oi\Desktop\ai-tools\skills
- Commit: 6eeb81b Merge branch 'main' of https://github.com/mattpocock/skills
- package.json: True
- pyproject.toml: False
- requirements.txt: False
- Cargo.toml: False
- go.mod: False
- Dockerfile: False

### Sinais de instalacao
## Quickstart (30-second setup) | 1. Run the skills.sh installer: | 2. Pick the skills you want, and which coding agents you want to install them on. **Make sure you select `/setup-matt-pocock-skills`**. | 3. Run `/setup-matt-pocock-skills` in your agent. It will: | - **[setup-matt-pocock-skills](./skills/engineering/setup-matt-pocock-skills/SKILL.md)** — Configure this repo for the engineering skills (issue tracker, triage labels, domain doc layout). Run once per repo before using the other engineering skills. | - **[setup-pre-commit](./skills/misc/setup-pre-commit/SKILL.md)** — Set up Husky pre-commit hooks with lint-staged, Prettier, type checking, and tests.

### Sinais de execucao
## Quickstart (30-second setup) | 1. Run the skills.sh installer: | npx skills@latest add mattpocock/skills | 3. Run `/setup-matt-pocock-skills` in your agent. It will: | These are my most popular skills. They help you align with the agent before you get started, and think deeply about the change you're making. Use them _every_ time you want to make a change. | **The Problem**: At the start of a project, devs and the people they're building the software for (the domain experts) are usually speaking different languages. | It's time to look at your feedback loops. Without feedback on how the code it produces actually runs, the agent will be flying blind. | And crucially, [`/improve-codebase-architecture`](./skills/engineering/improve-codebase-architecture/SKILL.md) helps you rescue a codebase that has become a ball of mud. I recommend running it on your codebase once every few days. | - **[setup-matt-pocock-skills](./skills/engineering/setup-matt-pocock-skills/SKILL.md)** — Configure this repo for the engineering skills (issue tracker, triage labels, domain doc layout). Run once per repo before using the other engineering skills. | - **[prototype](./skills/engineering/prototype/SKILL.md)** — Build a throwaway prototype to flesh out a design — either a runnable terminal app for state/business-logic questions, or several radically different UI variations toggleable from one route. | - **[git-guardrails-claude-code](./skills/misc/git-guardrails-claude-code/SKILL.md)** — Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, etc.) before they execute.

