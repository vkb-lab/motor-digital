# K-OS Codebase Memory MCP Installer Risk Audit

Status: auditoria de risco criada. Nenhum instalador executado.

## install.ps1
- Existe: True
- Tamanho: 5111
- Riscos detectados: network_download, path_or_environment_change, system_or_user_config, delete_operation

PREVIEW
# install.ps1 — One-line installer for codebase-memory-mcp (Windows).
#
# Usage: see README.md for install instructions.
#
# Environment:
#   CBM_DOWNLOAD_URL  Override base URL for downloads (for testing)

$ErrorActionPreference = "Stop"

# Enforce TLS 1.2+ (older PowerShell defaults to TLS 1.0 which GitHub rejects)
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13

$Repo = "DeusData/codebase-memory-mcp"
$InstallDir = "$env:LOCALAPPDATA\Programs\codebase-memory-mcp"
$BinName = "codebase-memory-mcp.exe"
$BaseUrl = if ($env:CBM_DOWNLOAD_URL) { $env:CBM_DOWNLOAD_URL } else { "https://github.com/$Repo/releases/latest/download" }

# Security: reject non-HTTPS download URLs (defense-in-depth)
if (-not $BaseUrl.StartsWith("https://") -and -not $BaseUrl.StartsWith("http://localhost") -and -not $BaseUrl.StartsWith("http://127.0.0.1")) {
    Write-Host "error: refusing non-HTTPS download URL: $BaseUrl" -ForegroundColor Red
    exit 1
}

# Detect variant from args (--ui or --standard)
$Variant = "standard"
$SkipConfig = $false
foreach ($arg in $args) {
    if ($arg -eq "--ui") { $Variant = "ui" }
    if ($arg -eq "--standard") { $Variant = "standard" }
    if ($arg -eq "--skip-config") { $SkipConfig = $true }
    if ($arg -like "--dir=*") { $InstallDir = $arg.Substring(6) }
}

Write-Host "codebase-memory-mcp installer (Windows)"
Write-Host "  variant: $Variant"
Write-Host "  target:  $InstallDir\$BinName"
Write-Host ""

# Build download URL
if ($Variant -eq "ui") {
    $Archive = "codebase-memory-mcp-ui-windows-amd64.zip"
} else {
    $Archive = "codebase-memory-mcp-windows-amd64.zip"
}
$Url = "$BaseUrl/$Archive"

# Download
$TmpDir = Join-Path ([System.IO.Path]::GetTempPath()) "cbm-install-$(Get-Random)"
New-Item -ItemType Directory -Path $TmpDir -Force | Out-Null

Write-Host "Downloading $Archive..."
try {
    Invoke-WebRequest -Uri $Url -OutFile "$TmpDir\$Archive" -UseBasicParsing
} catch {
    Write-Host "error: download failed: $_" -ForegroundColor Red
    Remove-Item -Recurse -Force $TmpDir -ErrorAction SilentlyContinue
    exit 1
}


# Checksum verification
$ChecksumUrl = "$BaseUrl/checksums.txt"
try {
    Invoke-WebRequest -Uri $ChecksumUrl -OutFile "$TmpDir\checksums.txt" -UseBasicParsing
    $checksumLine = Get-Content "$TmpDir\checksums.txt" | Where-Object { $_ -like "*$Archive*" }
    if ($checksumLine) {
        $expected = ($checksumLine -split '\s+')[0]
        $actual = (Get-FileHas

## scripts/setup-windows.ps1
- Existe: True
- Tamanho: 10754
- Riscos detectados: network_download, path_or_environment_change, system_or_user_config, mcp_client_config, delete_operation

PREVIEW
# codebase-memory-mcp setup script (Windows)
# Default: download pre-built native Windows binary
# -FromSource: build from source inside WSL (requires Go + gcc in WSL)

param(
    [switch]$FromSource,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

$Repo = "DeusData/codebase-memory-mcp"
$BinaryName = "codebase-memory-mcp"
$InstallDir = Join-Path $env:LOCALAPPDATA "codebase-memory-mcp"

# --- Helpers ---

function Write-Ok($msg)   { Write-Host "  $msg" -ForegroundColor Green }
function Write-Fail($msg)  { Write-Host "  $msg" -ForegroundColor Red }
function Write-Warn($msg)  { Write-Host "  $msg" -ForegroundColor Yellow }

function Read-SettingsJson($Path) {
    # PS5.1-compatible: ConvertFrom-Json returns PSCustomObject, not Hashtable.
    # We convert to ordered hashtable manually.
    if (-not (Test-Path $Path)) {
        return @{}
    }
    $raw = Get-Content $Path -Raw
    if (-not $raw -or $raw.Trim() -eq "") {
        return @{}
    }
    $obj = $raw | ConvertFrom-Json
    $ht = [ordered]@{}
    foreach ($prop in $obj.PSObject.Properties) {
        if ($prop.Value -is [System.Management.Automation.PSCustomObject]) {
            $inner = [ordered]@{}
            foreach ($p in $prop.Value.PSObject.Properties) {
                $inner[$p.Name] = $p.Value
            }
            $ht[$prop.Name] = $inner
        } else {
            $ht[$prop.Name] = $prop.Value
        }
    }
    return $ht
}

function Write-SettingsJson($Path, $Settings) {
    # Back up existing file before writing
    if (Test-Path $Path) {
        Copy-Item $Path "$Path.bak" -Force
    }
    $Settings | ConvertTo-Json -Depth 10 | Set-Content $Path -Encoding UTF8
}

function Configure-ClaudeCode($McpConfig) {
    Write-Host ""
    $answer = Read-Host "Configure Claude Code to use codebase-memory-mcp? [y/N]"

    if ($answer -match '^[Yy]$') {
        $settingsPath = Join-Path $env:USERPROFILE ".claude\settings.json"
        $settingsDir = Split-Path $settingsPath -Parent

        if (-not (Test-Path $settingsDir)) {
            New-Item -ItemType Directory -Path $settingsDir -Force | Out-Null
        }

        $settings = Read-SettingsJson $settingsPath

        if (-not $settings.Contains("mcpServers")) {
            $settings["mcpServers"] = [ordered]@{}
        }

        $settings["mcpServers"]["codebase-memory-mcp"] = $McpConfig
        Write-SettingsJson $settingsPath $settings
        Write-Ok "Updated $settingsPath"
    } else {
        Write-Host ""
        Write-Ho

## server.json
- Existe: True
- Tamanho: 895
- Riscos detectados: network_download, system_or_user_config

PREVIEW
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.github.DeusData/codebase-memory-mcp",
  "title": "Codebase Memory",
  "description": "Codebase knowledge graph for AI agents \u2014 159 languages, sub-ms queries, 99% fewer tokens.",
  "repository": {
    "url": "https://github.com/DeusData/codebase-memory-mcp",
    "source": "github"
  },
  "websiteUrl": "https://deusdata.github.io/codebase-memory-mcp/",
  "version": "0.8.1",
  "packages": [
    {
      "registryType": "npm",
      "identifier": "codebase-memory-mcp",
      "version": "0.8.1",
      "runtimeHint": "npx",
      "transport": {
        "type": "stdio"
      }
    },
    {
      "registryType": "pypi",
      "identifier": "codebase-memory-mcp",
      "version": "0.8.1",
      "runtimeHint": "uvx",
      "transport": {
        "type": "stdio"
      }
    }
  ]
}


## pkg/npm/package.json
- Existe: True
- Tamanho: 920
- Riscos detectados: network_download, mcp_client_config

PREVIEW
{
  "name": "codebase-memory-mcp",
  "version": "0.8.1",
  "description": "Fast code intelligence engine for AI coding agents — single static binary MCP server",
  "mcpName": "io.github.DeusData/codebase-memory-mcp",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "git+https://github.com/DeusData/codebase-memory-mcp.git"
  },
  "homepage": "https://github.com/DeusData/codebase-memory-mcp",
  "bugs": {
    "url": "https://github.com/DeusData/codebase-memory-mcp/issues"
  },
  "keywords": [
    "mcp",
    "claude",
    "code-intelligence",
    "codebase",
    "memory",
    "ai",
    "llm",
    "tree-sitter"
  ],
  "bin": {
    "codebase-memory-mcp": "./bin.js"
  },
  "scripts": {
    "postinstall": "node install.js"
  },
  "engines": {
    "node": ">=18"
  },
  "os": ["linux", "darwin", "win32"],
  "cpu": ["x64", "arm64"],
  "files": [
    "bin.js",
    "install.js",
    "README.md"
  ]
}


## pkg/go/go.mod
- Existe: True
- Tamanho: 65
- Riscos detectados: none

PREVIEW
module github.com/DeusData/codebase-memory-mcp/pkg/go

go 1.26.1


## Dockerfile
- Existe: False
- Tamanho: 0
- Riscos detectados: missing

PREVIEW


## pkg/glama/Dockerfile
- Existe: True
- Tamanho: 1394
- Riscos detectados: network_download, delete_operation

PREVIEW
# Glama MCP directory (glama.ai) check image — NOT required to run the tool.
#
# codebase-memory-mcp needs NO Docker to run. This image exists only so Glama
# can build a sandbox, launch the stdio MCP server, and run its introspection
# checks, which power the directory's score badge. The same image is exercised
# locally and in CI by pkg/glama/verify.sh to guard against drift.
#
# We pull the "-portable" release asset, which is fully statically linked
# (gcc -static) — unlike the standard asset, which dynamically links glibc/
# libstdc++ and would fail on an older base. Because it's static, the runtime
# base image is arbitrary. TARGETARCH is amd64 / arm64, matching the asset names.

FROM debian:bookworm-slim AS fetch
ARG TARGETARCH
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates \
 && curl -fsSL "https://github.com/DeusData/codebase-memory-mcp/releases/latest/download/codebase-memory-mcp-linux-${TARGETARCH}-portable.tar.gz" \
      | tar -xz -C /tmp codebase-memory-mcp LICENSE THIRD_PARTY_NOTICES.md \
 && chmod +x /tmp/codebase-memory-mcp \
 && rm -rf /var/lib/apt/lists/*

FROM debian:bookworm-slim
COPY --from=fetch /tmp/codebase-memory-mcp /usr/local/bin/codebase-memory-mcp
COPY --from=fetch /tmp/LICENSE /tmp/THIRD_PARTY_NOTICES.md /usr/share/doc/codebase-memory-mcp/
ENV CBM_CACHE_DIR=/tmp/cbm
ENTRYPOINT ["codebase-memory-mcp"]


## test-infrastructure/Dockerfile
- Existe: True
- Tamanho: 786
- Riscos detectados: path_or_environment_change, dependency_or_build, delete_operation

PREVIEW
# Mirrors the Ubuntu CI environment exactly:
#   - Ubuntu 24.04 (same as GitHub Actions ubuntu-latest / ubuntu-24.04-arm)
#   - GCC (system default) with ASan + UBSan + LeakSanitizer
#   - libsqlite3-dev + zlib1g-dev (same as CI "Install deps" step)
#
# Build:  docker build -t cbm-test test-infrastructure/
# Run:    docker run --rm -v $(pwd):/src cbm-test

FROM ubuntu:noble

# Minimal: gcc + zlib only. sqlite3 is vendored (compiled from source with ASan).
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make \
    zlib1g-dev \
    pkg-config \
    python3 \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

# Default: run test.sh with GCC (mirrors CI exactly)
ENTRYPOINT ["scripts/test.sh"]
CMD ["CC=gcc", "CXX=g++"]

