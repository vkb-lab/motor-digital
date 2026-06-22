# K-OS Codebase Memory MCP Local Inspect

Status: auditoria local criada. Nada instalado.

## Politica
- Nenhuma instalacao executada
- Nenhum MCP conectado
- Nenhuma IA conectada
- Nenhuma API key usada
- Nenhum gasto

## Sinais encontrados
- EXE: 0
- PS1: 4
- server.json: 1
- Dockerfile: 6
- Cargo.toml: 0
- go.mod: 1
- package.json: 4

## Hints do README
- # codebase-memory-mcp
- [![GitHub Release](https://img.shields.io/github/v/release/DeusData/codebase-memory-mcp?style=flat&color=blue)](https://github.com/DeusData/codebase-memory-mcp/releases/latest)
- [![CI](https://img.shields.io/github/actions/workflow/status/DeusData/codebase-memory-mcp/dry-run.yml?label=CI)](https://github.com/DeusData/codebase-memory-mcp/actions/workflows/dry-run.yml)
- [![Tests](https://img.shields.io/badge/tests-5604_passing-brightgreen)](https://github.com/DeusData/codebase-memory-mcp)
- [![Languages](https://img.shields.io/badge/languages-158-orange)](https://github.com/DeusData/codebase-memory-mcp)
- [![Agents](https://img.shields.io/badge/agents-11-purple)](https://github.com/DeusData/codebase-memory-mcp)
- [![Pure C](https://img.shields.io/badge/pure_C-zero_dependencies-blue)](https://github.com/DeusData/codebase-memory-mcp)
- [![Platform](https://img.shields.io/badge/macOS_%7C_Linux_%7C_Windows-supported-lightgrey)](https://github.com/DeusData/codebase-memory-mcp/releases/latest)
- [![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/DeusData/codebase-memory-mcp/badge)](https://scorecard.dev/viewer/?uri=github.com/DeusData/codebase-memory-mcp)
- [![VirusTotal](https://img.shields.io/badge/VirusTotal-scanned_every_release-brightgreen?logo=virustotal)](https://github.com/DeusData/codebase-memory-mcp/releases/latest)
- **The fastest and most efficient code intelligence engine for AI coding agents.** Full-indexes an average repository in milliseconds, the Linux kernel (28M LOC, 75K files) in 3 minutes. Answers structural queries in under 1ms. Ships as a single static binary for macOS, Linux, and Windows — download, run `install`, done.
- High-quality parsing through [tree-sitter](https://tree-sitter.github.io/tree-sitter/) AST analysis across all 158 languages, enhanced with [**Hybrid LSP** semantic type resolution](#hybrid-lsp) for Python, TypeScript / JavaScript / JSX / TSX, PHP, C#, Go, C, C++, Java, Kotlin, and Rust — producing a persistent knowledge graph of functions, classes, call chains, HTTP routes, and cross-service links. 14 MCP tools. Zero dependencies. Plug and play across 11 coding agents.
- > **Research** — The design and benchmarks behind this project are described in the preprint [*Codebase-Memory: Tree-Sitter-Based Knowledge Graphs for LLM Code Exploration via MCP*](https://arxiv.org/abs/2603.27277) (arXiv:2603.27277). Evaluated across 31 real-world repositories: 83% answer quality, 10× fewer tokens, 2.1× fewer tool calls vs. file-by-file exploration.
- > **Security & Trust** — This tool reads your codebase and writes to your agent configuration files. That is what it is designed to do. If you prefer to audit before running, the [full source is here](https://github.com/DeusData/codebase-memory-mcp) — every release binary is signed, checksummed, and scanned by 70+ antivirus engines. All processing happens 100% locally; your code never leaves your machine. Found a security issue? We want to know — see [SECURITY.md](SECURITY.md). Security is Priority #1 for us.
- <img src="docs/graph-ui-screenshot.png" alt="Graph visualization UI showing the codebase-memory-mcp knowledge graph" width="800">
- <em>Built-in 3D graph visualization (UI variant) — explore your knowledge graph at localhost:9749</em>
- ## Why codebase-memory-mcp
- - **Extreme indexing speed** — Linux kernel (28M LOC, 75K files) in 3 minutes. RAM-first pipeline: LZ4 compression, in-memory SQLite, fused Aho-Corasick pattern matching. Memory released after indexing.
- - **Plug and play** — single static binary for macOS (arm64/amd64), Linux (arm64/amd64), and Windows (amd64). No Docker, no runtime dependencies, no API keys. Download → `install` → restart agent → done.
- - **158 languages** — vendored tree-sitter grammars compiled into the binary. Nothing to install, nothing that breaks.
- - **120x fewer tokens** — 5 structural queries: ~3,400 tokens vs ~412,000 via file-by-file search. One graph query replaces dozens of grep/read cycles.
- - **11 agents, one command** — `install` auto-detects Claude Code, Codex CLI, Gemini CLI, Zed, OpenCode, Antigravity, Aider, KiloCode, VS Code, OpenClaw, and Kiro — configures MCP entries, instruction files, and pre-tool hooks for each.
- - **Built-in graph visualization** — 3D interactive UI at `localhost:9749` (optional UI binary variant).
- - **Infrastructure-as-code indexing** — Dockerfiles, Kubernetes manifests, and Kustomize overlays indexed as graph nodes with cross-references. `Resource` nodes for K8s kinds, `Module` nodes for Kustomize overlays with `IMPORTS` edges to referenced resources.
- - **14 MCP tools** — search, trace, architecture, impact analysis, Cypher queries, dead code detection, cross-service HTTP linking, ADR management, and more.
- **One-line install** (macOS / Linux):
- curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash
- With graph visualization UI:
- curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash -s -- --ui
- **Windows** (PowerShell):
- ```powershell
- # 1. Download the installer
- Invoke-WebRequest -Uri https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.ps1 -OutFile install.ps1
- notepad install.ps1
- .\install.ps1
- Options: `--ui` (graph visualization), `--skip-config` (binary only, no agent setup), `--dir=<path>` (custom location).
- Restart your coding agent. Say **"Index this project"** — done.
- <summary>Manual install</summary>
- 1. **Download** the archive for your platform from the [latest release](https://github.com/DeusData/codebase-memory-mcp/releases/latest):
- - `codebase-memory-mcp-<os>-<arch>.tar.gz` (macOS/Linux) or `.zip` (Windows) — standard
- - `codebase-memory-mcp-ui-<os>-<arch>.tar.gz` / `.zip` — with graph visualization
- 2. **Extract and install** (each archive includes `install.sh` or `install.ps1`):
- tar xzf codebase-memory-mcp-*.tar.gz
- ./install.sh
- Windows (PowerShell):
- ```powershell
- Expand-Archive codebase-memory-mcp-windows-amd64.zip -DestinationPath .
- .\install.ps1
- The `install` command automatically strips macOS quarantine attributes and ad-hoc signs the binary — no manual `xattr`/`codesign` needed.
- The `install` command auto-detects all installed coding agents and configures MCP server entries, instruction files, skills, and pre-tool hooks for each.
- ### Graph Visualization UI
- If you downloaded the `ui` variant:
- codebase-memory-mcp --ui=true --port=9749
- Open `http://localhost:9749` in your browser. The UI runs as a background thread alongside the MCP server — it's available whenever your agent is connected.
- ### Auto-Index
- Enable automatic indexing on MCP session start:
- codebase-memory-mcp config set auto_index true
- When enabled, new projects are indexed automatically on first connection. Previously-indexed projects are registered with the background watcher for ongoing git-based change detection. Configurable file limit: `config set auto_index_limit 50000`.
- codebase-memory-mcp update
- The MCP server also checks for updates on startup and notifies on the first tool call if a newer release is available.
- ### Uninstall
- codebase-memory-mcp uninstall
- Removes all agent configs, skills, hooks, and instructions. Does not remove the binary or SQLite databases.
- ### Graph & analysis
- - **Call graph**: Resolves function calls across files and packages (import-aware, type-inferred)
- - **Semantic search** (`semantic_query`): vector search across the entire graph, powered by bundled Nomic `nomic-embed-code` embeddings (40K tokens, 768d int8) compiled into the binary — no API key, no Ollama, no Docker. 11-signal combined scoring (TF-IDF, RRI, API/Type/Decorator signatures, AST profiles, data flow, Halstead-lite, MinHash, module proximity, graph diffusion).
- - **Structural search** (`search_graph`): regex name patterns, label filters, min/max degree, file scoping
- - **Code search** (`search_code`): graph-augmented grep over indexed files only
- - **gRPC, GraphQL, tRPC** service detection with protobuf Route extraction
- - **`CROSS_*` edges** link nodes across multiple repos indexed under the same store
- - **Cross-repo architecture summary** combining services, routes, and dependencies across the indexed fleet
- ### Indexing pipeline
- - **158 vendored tree-sitter grammars** compiled into the binary
- - **Infrastructure-as-code indexing** — Dockerfiles, Kubernetes manifests, Kustomize overlays as graph nodes
- - **[Hybrid LSP semantic type resolution](#hybrid-lsp)** for Python, TypeScript / JavaScript / JSX / TSX, PHP, C#, Go, C, C++, Java, Kotlin, and Rust — a lightweight C implementation of language type-resolution algorithms, structurally inspired by and compatible with major language servers including tsserver / typescript-go, pyright, gopls, Roslyn, Eclipse JDT, and rust-analyzer (parameter binding, return-type inference, generic substitution, JSX component dispatch, JSDoc inference for plain JS files, namespace + trait + late-static-binding resolution for PHP, file-scoped namespaces + records + LINQ method syntax for C#, class-hierarchy + overload + lambda resolution for Java, extension-function + scope-function resolution for Kotlin, trait-method + UFCS resolution for Rust)
- - **Single static binary, zero infrastructure**: SQLite-backed, persists to `~/.cache/codebase-memory-mcp/`
- - **Auto-sync**: Background watcher detects file changes and re-indexes automatically
- - **Route nodes**: REST endpoints are first-class graph entities
- - **CLI mode**: `codebase-memory-mcp cli search_graph '{"name_pattern": ".*Handler.*"}'`
- - **Available on**: npm, PyPI, Homebrew, Scoop, Winget, Chocolatey, AUR, `go install`

## Recomendacao
Primeiro testar Codebase Memory MCP em modo isolado, sem configurar agente e sem alterar o K-OS.
