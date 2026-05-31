from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "ops" / "k_os_roadmap_planner_release_notes_core.py"
REPORT_PATH = PROJECT_ROOT / "reports" / "roadmap" / "latest_roadmap_release_report.json"
ROADMAP_PATH = PROJECT_ROOT / "reports" / "roadmap" / "latest_internal_roadmap_snapshot.json"
NOTES_PATH = PROJECT_ROOT / "reports" / "roadmap" / "latest_release_notes_draft.json"
POLICY_PATH = PROJECT_ROOT / "config" / "roadmap" / "k_os_roadmap_release_policy.json"

st.set_page_config(page_title="K-OS Roadmap Planner", layout="wide")

st.title("K-OS Roadmap Planner and Release Notes Core")
st.caption("Checkpoint 035 - roadmap interno, releases, features por versão e notas de release.")

st.warning(
    "Roadmap local. Nenhuma release é publicada. Nenhuma promessa externa é feita automaticamente."
)


def python_exe() -> str:
    candidates = [
        PROJECT_ROOT / "venv" / "Scripts" / "python.exe",
        PROJECT_ROOT / ".venv" / "Scripts" / "python.exe",
    ]
    for item in candidates:
        if item.exists():
            return str(item)
    return "python"


def run(args: list[str]) -> None:
    completed = subprocess.run(
        [python_exe(), str(SCRIPT), *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    st.code(" ".join(completed.args), language="powershell")

    if completed.stdout:
        st.code(completed.stdout, language="json")

    if completed.stderr:
        st.code(completed.stderr, language="text")

    if completed.returncode == 0:
        st.success("OK")
    else:
        st.error(f"Falhou: {completed.returncode}")


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Dashboard", "Release", "Feature", "Status", "Release Notes", "Policy"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Inicializar Roadmap", type="primary"):
            run(["--mode", "init"])

    with c2:
        if st.button("Criar demo"):
            run(["--mode", "create-demo"])

    with c3:
        if st.button("Auditar"):
            run(["--mode", "audit"])

    if REPORT_PATH.exists():
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))
        metrics = report.get("metrics", {})

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Releases", metrics.get("release_count", 0))

        with m2:
            st.metric("Feature links", metrics.get("release_feature_link_count", 0))

        with m3:
            st.metric("Release notes", metrics.get("release_notes_count", 0))

        with m4:
            st.metric("Public sensitive", metrics.get("public_sensitive_release_count", 0))

        st.subheader("Releases")
        st.dataframe(report.get("releases", []), use_container_width=True)

        st.subheader("Feature links")
        st.dataframe(report.get("release_feature_links", []), use_container_width=True)

        st.subheader("Release notes")
        st.dataframe(report.get("release_notes", []), use_container_width=True)

    if ROADMAP_PATH.exists():
        st.subheader("Internal roadmap snapshot")
        st.json(json.loads(ROADMAP_PATH.read_text(encoding="utf-8-sig")))

with tab2:
    title = st.text_input("Título da release", value="K-OS SaaS Evolution Release")
    version_label = st.text_input("Versão", value="v0.35-internal")
    release_type = st.selectbox("Tipo", ["patch", "minor", "major", "experiment", "security", "commercial"])
    channel = st.selectbox("Canal", ["internal", "private_beta", "customer_pilot", "public"])
    target_date = st.text_input("Target date YYYY-MM-DD", value="")
    owner = st.text_input("Owner", value="k_os_operator")

    if st.button("Criar release", type="primary"):
        run([
            "--mode", "create-release",
            "--title", title,
            "--version-label", version_label,
            "--release-type", release_type,
            "--channel", channel,
            "--target-date", target_date,
            "--owner", owner
        ])

with tab3:
    release_id = st.text_input("Release ID")
    feature_id = st.text_input("Feature ID")
    reason = st.text_input("Motivo", value="manual_release_planning")

    if st.button("Adicionar feature à release", type="primary"):
        run(["--mode", "add-feature", "--release-id", release_id, "--feature-id", feature_id, "--reason", reason])

with tab4:
    status_release_id = st.text_input("Release ID para status")
    status = st.selectbox(
        "Status",
        [
            "draft",
            "internal_review",
            "planned",
            "in_progress",
            "qa_review",
            "ready_internal",
            "released_internal",
            "public_draft",
            "approved_for_manual_publish",
            "published_manually",
            "cancelled",
            "archived"
        ]
    )
    status_reason = st.text_input("Razão do status", value="manual_operator_review")

    if st.button("Atualizar status", type="primary"):
        run(["--mode", "set-release-status", "--release-id", status_release_id, "--status", status, "--reason", status_reason])

with tab5:
    notes_release_id = st.text_input("Release ID para notas")
    audience = st.selectbox("Audience", ["internal", "public_draft"])

    if st.button("Gerar notas de release", type="primary"):
        run(["--mode", "generate-release-notes", "--release-id", notes_release_id, "--audience", audience])

    if NOTES_PATH.exists():
        st.subheader("Último draft")
        st.json(json.loads(NOTES_PATH.read_text(encoding="utf-8-sig")))

with tab6:
    if POLICY_PATH.exists():
        st.json(json.loads(POLICY_PATH.read_text(encoding="utf-8-sig")))
    else:
        st.info("Policy ainda não encontrada.")