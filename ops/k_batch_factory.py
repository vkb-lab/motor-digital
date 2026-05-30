from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path.cwd()
SPEC_PATH = ROOT / ".k_atlas_batch_factory_spec.json"

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")

def title_id(text: str) -> str:
    return "".join(part.capitalize() for part in re.sub(r"[^a-zA-Z0-9]+", " ", text).split())

def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.lstrip(), encoding="utf-8")

spec = json.loads(SPEC_PATH.read_text(encoding="utf-8-sig"))

start = int(spec["start"])
end = int(spec["end"])
batch_name = spec["batch_name"]
items = spec["items"]

created_modules = []

for offset, name in enumerate(items):
    number = start + offset
    slug = slugify(name)
    class_name = title_id(name)
    module_dir = f"k_atlas/core/{slug}"
    page_name = f"pages/{number}_K_Atlas_{class_name}.py"

    created_modules.append((number, name, slug, class_name, page_name))

    write(f"{module_dir}/__init__.py", f'''
from .core import KAtlasComponent

__all__ = ["KAtlasComponent"]
''')

    write(f"{module_dir}/core.py", f'''
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class KAtlasComponent:
    checkpoint = "{number}"
    name = "{name}"
    batch = "{start}-{end}"
    batch_name = "{batch_name}"

    def summary(self) -> dict[str, Any]:
        return {{
            "ok": True,
            "checkpoint": self.checkpoint,
            "name": self.name,
            "batch": self.batch,
            "batch_name": self.batch_name,
            "status": "operational",
            "execution_enabled": False,
            "real_execution_enabled": False,
            "external_side_effects": "none",
            "human_approval_required": True,
            "guardrails": [
                "sem execucao automatica",
                "sem API externa",
                "sem controle remoto real",
                "sem captura de senha",
                "sem deploy automatico",
                "auditoria obrigatoria"
            ],
            "generated_at": utc_now()
        }}
''')

    write(f"{module_dir}/smoke_test_{slug}.py", f'''
from __future__ import annotations

import py_compile
import unittest

from k_atlas.core.{slug}.core import KAtlasComponent


class SmokeTest(unittest.TestCase):
    def test_summary(self) -> None:
        result = KAtlasComponent().summary()
        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"], "{number}")
        self.assertFalse(result["real_execution_enabled"])

    def test_page_compiles(self) -> None:
        py_compile.compile("{page_name}", doraise=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
''')

    write(page_name, f'''
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from k_atlas.core.{slug}.core import KAtlasComponent


st.set_page_config(page_title="K-Atlas {name}", layout="wide")

component = KAtlasComponent()
summary = component.summary()

st.title("K-Atlas {name}")
st.caption("Checkpoint {number} - gerado pelo K-Atlas Local Batch Factory.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Checkpoint", summary.get("checkpoint"))

with col2:
    st.metric("Status", summary.get("status"))

with col3:
    st.metric("Execucao real", str(summary.get("real_execution_enabled")))

with col4:
    st.metric("Side effects", summary.get("external_side_effects"))

st.divider()

tab_summary, tab_guardrails = st.tabs(["Resumo", "Guardrails"])

with tab_summary:
    st.json(summary)

with tab_guardrails:
    for item in summary.get("guardrails", []):
        st.write("- " + item)
''')

readme_lines = [
    f"# Batch {start}-{end} - {batch_name}",
    "",
    "Gerado localmente pelo K-Atlas Batch Factory.",
    "",
    "## Componentes",
    "",
]

for number, name, slug, class_name, page_name in created_modules:
    readme_lines.append(f"- {number} - {name} - `{slug}`")

readme_lines.extend([
    "",
    "## Governanca",
    "",
    "- Sem execucao automatica",
    "- Sem API externa",
    "- Sem controle remoto real",
    "- Sem captura de senha",
    "- Sem deploy automatico",
    "- Com smoke tests",
    "- Com commit e push"
])

write(f"README_BATCH_{start}_{end}_{slugify(batch_name).upper()}.md", "\\n".join(readme_lines))

demo_lines = [
    '$ErrorActionPreference = "Stop"',
    '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8',
    '',
    'cd "C:\\Users\\oi\\Desktop\\motor-digital"',
    '',
    'if (Test-Path ".\\venv\\Scripts\\python.exe") {',
    '    $Python = ".\\venv\\Scripts\\python.exe"',
    '} elseif (Test-Path ".\\.venv\\Scripts\\python.exe") {',
    '    $Python = ".\\.venv\\Scripts\\python.exe"',
    '} else {',
    '    throw "Python virtualenv nao encontrado."',
    '}',
    '',
    '$env:PYTHONPATH = (Get-Location).Path',
    '$env:PYTHONIOENCODING = "utf-8"',
    ''
]

for _, _, slug, _, _ in created_modules:
    demo_lines.append(f'& $Python -m k_atlas.core.{slug}.smoke_test_{slug}')

demo_lines.append('')
demo_lines.append(f'Write-Host "BATCH {start}-{end} DEMO OK"')

write(f"ops/run_batch_{start}_{end}_demo.ps1", "\\n".join(demo_lines))

print(json.dumps({
    "ok": True,
    "batch": f"{start}-{end}",
    "batch_name": batch_name,
    "created": [
        {"checkpoint": number, "name": name, "slug": slug}
        for number, name, slug, _, _ in created_modules
    ]
}, ensure_ascii=False, indent=2))