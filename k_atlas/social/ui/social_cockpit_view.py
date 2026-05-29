# -*- coding: utf-8 -*-
"""K-Social cockpit UI layer.

This module prepares dashboard data and optional Streamlit rendering for K-Social.
It does not publish content, does not call external APIs and does not operate browsers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_SNAPSHOT_PATH = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "social_dashboard_snapshot.json"
)

DEFAULT_REPORT_JSON_PATH = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "social_daily_report.json"
)

DEFAULT_REPORT_MD_PATH = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "social_daily_report.md"
)


def _split_lines(value: str) -> List[str]:
    """Split multiline text into clean list items."""

    return [
        item.strip()
        for item in value.splitlines()
        if item.strip()
    ]


def _split_channels(value: str) -> List[str]:
    """Split channel input using commas or lines."""

    raw = value.replace(",", "\n")
    return [
        item.strip()
        for item in raw.splitlines()
        if item.strip()
    ]


def load_social_snapshot(snapshot_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load the K-Social dashboard snapshot from JSON."""

    path = Path(snapshot_path) if snapshot_path else DEFAULT_SNAPSHOT_PATH

    if not path.exists():
        return {
            "system": "K-Social Cockpit Snapshot",
            "snapshot_found": False,
            "message": "Snapshot social ainda nao foi gerado.",
            "total_operations": 0,
            "ready_for_review": 0,
            "blocked_operations": 0,
            "total_content_items": 0,
            "publication_permission": False,
            "external_api_used": False,
            "human_review_required": True,
            "operations": [],
        }

    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    data["snapshot_found"] = True
    return data


def load_social_report(
    report_json_path: Optional[Path] = None,
    report_md_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Load the K-Social daily report from JSON and Markdown."""

    json_path = Path(report_json_path) if report_json_path else DEFAULT_REPORT_JSON_PATH
    md_path = Path(report_md_path) if report_md_path else DEFAULT_REPORT_MD_PATH

    result: Dict[str, Any] = {
        "report_found": False,
        "json_found": json_path.exists(),
        "markdown_found": md_path.exists(),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "json": {},
        "markdown": "",
    }

    if json_path.exists():
        with json_path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)

        if isinstance(data, dict):
            result["json"] = data

    if md_path.exists():
        result["markdown"] = md_path.read_text(encoding="utf-8-sig")

    result["report_found"] = bool(result["json_found"] or result["markdown_found"])
    return result


def build_social_cockpit_summary(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Build a compact summary for cockpit rendering."""

    operations = snapshot.get("operations", [])

    return {
        "system": snapshot.get("system", "K-Social Cockpit Snapshot"),
        "snapshot_found": snapshot.get("snapshot_found", True),
        "message": snapshot.get("message", ""),
        "total_operations": int(snapshot.get("total_operations", len(operations))),
        "ready_for_review": int(snapshot.get("ready_for_review", 0)),
        "blocked_operations": int(snapshot.get("blocked_operations", 0)),
        "total_content_items": int(snapshot.get("total_content_items", 0)),
        "publication_permission": bool(snapshot.get("publication_permission", False)),
        "external_api_used": bool(snapshot.get("external_api_used", False)),
        "human_review_required": bool(snapshot.get("human_review_required", True)),
        "operations": operations,
    }


def build_social_report_summary(report: Dict[str, Any]) -> Dict[str, Any]:
    """Build compact report metadata for cockpit rendering."""

    report_json = report.get("json", {})
    summary = report_json.get("summary", {}) if isinstance(report_json, dict) else {}

    return {
        "report_found": bool(report.get("report_found", False)),
        "json_found": bool(report.get("json_found", False)),
        "markdown_found": bool(report.get("markdown_found", False)),
        "generated_at": report_json.get("generated_at", "nao informado"),
        "total_operations": int(summary.get("total_operations", 0)),
        "ready_for_review": int(summary.get("ready_for_review", 0)),
        "blocked_operations": int(summary.get("blocked_operations", 0)),
        "total_content_items": int(summary.get("total_content_items", 0)),
        "risks": report_json.get("risks", []),
        "next_actions": report_json.get("next_actions", []),
        "markdown": report.get("markdown", ""),
    }


def render_social_operation_builder() -> None:
    """Render a safe operation builder form in Streamlit."""

    try:
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError("Streamlit nao esta instalado neste ambiente.") from exc

    from k_atlas.social.campaign_factory.social_operation_builder import SocialOperationBuilder

    st.subheader("Criar nova operacao social supervisionada")
    st.caption("Este formulario gera rascunho local. Nao publica, nao chama API e exige revisao humana.")

    with st.form("k_social_operation_builder_form"):
        product = st.text_input("Produto", value="BRICS Paraguay Autos")
        market = st.text_input("Mercado", value="marketplace automotivo Paraguai-Brasil")
        objective = st.text_input(
            "Objetivo",
            value="validar campanha local supervisionada para captacao inicial",
        )

        personas_text = st.text_area(
            "Personas",
            value=(
                "compradores brasileiros interessados em carros no Paraguai\n"
                "lojistas paraguaios que precisam melhorar anuncios\n"
                "investidores buscando oportunidades automotivas regionais"
            ),
            height=120,
        )

        channels_text = st.text_input("Canais", value="Instagram, Facebook, WhatsApp")
        duration_days = st.number_input("Duracao em dias", min_value=1, max_value=90, value=5)

        key_messages_text = st.text_area(
            "Mensagens principais",
            value=(
                "anuncios automotivos mais claros e confiaveis\n"
                "revisao humana antes de qualquer publicacao\n"
                "ponte comercial entre Paraguai e Brasil com mais organizacao"
            ),
            height=120,
        )

        format_type = st.selectbox("Formato", ["reel", "post", "story", "video", "imagem", "anuncio"])
        brand_tone = st.text_input("Tom da marca", value="premium, confiavel e direto")
        region = st.text_input("Regiao", value="Paraguai e Brasil")
        language = st.text_input("Idioma", value="pt-BR")
        seasonal_context = st.text_input(
            "Contexto sazonal",
            value="campanha inicial de validacao comercial",
        )

        submitted = st.form_submit_button("Gerar operacao supervisionada")

    if submitted:
        request = {
            "request_name": "cockpit_social_operation",
            "owner": "K-Atlas Operator",
            "product": product,
            "market": market,
            "personas": _split_lines(personas_text),
            "objective": objective,
            "channels": _split_channels(channels_text),
            "duration_days": int(duration_days),
            "key_messages": _split_lines(key_messages_text),
            "format_type": format_type,
            "brand_tone": brand_tone,
            "region": region,
            "language": language,
            "seasonal_context": seasonal_context,
        }

        try:
            builder = SocialOperationBuilder()
            result = builder.run_from_request_data(request)
            st.success("Operacao social criada e enviada para revisao humana.")
            st.write("Arquivo:", result["operation_file"])
            st.write("Operacoes no snapshot:", result["snapshot_total_operations"])
            st.write("Publicacao automatica:", result["publication_permission"])
            st.info("Atualize a pagina para ver as metricas atualizadas.")
        except Exception as exc:
            st.error("Falha ao criar operacao social.")
            st.caption(str(exc))


def render_social_cockpit(snapshot_path: Optional[Path] = None) -> None:
    """Render K-Social dashboard section in Streamlit."""

    try:
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError("Streamlit nao esta instalado neste ambiente.") from exc

    snapshot = load_social_snapshot(snapshot_path)
    summary = build_social_cockpit_summary(snapshot)

    st.subheader("K-Social Intelligence System")
    try:
        from k_atlas.social.ui.social_command_center_view import render_social_command_center

        render_social_command_center()
        st.divider()
    except Exception as command_center_error:
        st.warning("K-Social Command Center ainda nao foi carregado.")
        st.caption(str(command_center_error))


    with st.expander("Nova operacao social"):
        render_social_operation_builder()

    if not summary["snapshot_found"]:
        st.info(summary.get("message", "Snapshot social ainda nao foi gerado."))
        return

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Operacoes", summary["total_operations"])
    col2.metric("Para revisao", summary["ready_for_review"])
    col3.metric("Bloqueadas", summary["blocked_operations"])
    col4.metric("Itens", summary["total_content_items"])

    st.caption("Publicacao automatica: bloqueada")
    st.caption("APIs externas: bloqueadas neste checkpoint")
    st.caption("Revisao humana: obrigatoria")

    operations = summary["operations"]

    if not operations:
        st.warning("Nenhuma operacao social encontrada.")
    else:
        for operation in operations:
            with st.expander(operation.get("product", "Produto nao informado")):
                st.write("Mercado:", operation.get("market", "nao informado"))
                st.write("Objetivo:", operation.get("objective", "nao informado"))
                st.write("Status:", operation.get("operation_status", "unknown"))
                st.write("Auditoria:", operation.get("audit_status", "unknown"))
                st.write("Canais:", ", ".join(operation.get("channels", [])))
                st.write("Duracao:", operation.get("duration_days", 0), "dias")
                st.write("Itens de conteudo:", operation.get("content_items", 0))
                st.write("Revisao humana obrigatoria:", operation.get("human_review_required", True))
                st.write("Permissao de publicacao:", operation.get("publication_permission", False))

    try:
        from k_atlas.social.ui.social_approval_view import render_social_approval_queue

        st.divider()
        render_social_approval_queue()
    except Exception as approval_error:
        st.warning("Fila de aprovacao humana ainda nao foi carregada.")
        st.caption(str(approval_error))

    try:
        from k_atlas.social.ui.social_content_refinement_view import render_social_content_refinement_queue

        st.divider()
        render_social_content_refinement_queue()
    except Exception as refinement_error:
        st.warning("Fila de refinamento criativo ainda nao foi carregada.")
        st.caption(str(refinement_error))

    try:
        from k_atlas.social.ui.social_refinement_outputs_view import render_social_refinement_outputs

        st.divider()
        render_social_refinement_outputs()
    except Exception as outputs_error:
        st.warning("Refinamentos criativos ainda nao foram carregados.")
        st.caption(str(outputs_error))

    try:
        from k_atlas.social.ui.social_campaign_packages_view import render_social_campaign_packages

        st.divider()
        render_social_campaign_packages()
    except Exception as packages_error:
        st.warning("Pacotes de campanha ainda nao foram carregados.")
        st.caption(str(packages_error))

    try:
        from k_atlas.social.ui.social_campaign_package_approval_view import render_social_campaign_package_approval_queue

        st.divider()
        render_social_campaign_package_approval_queue()
    except Exception as package_approval_error:
        st.warning("Aprovacao final de pacotes ainda nao foi carregada.")
        st.caption(str(package_approval_error))

    report = load_social_report()
    report_summary = build_social_report_summary(report)

    st.divider()
    st.subheader("Relatorio Diario K-Social")

    if not report_summary["report_found"]:
        st.info("Relatorio diario ainda nao foi gerado.")
        return

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Operacoes no relatorio", report_summary["total_operations"])
    col_b.metric("Riscos", len(report_summary["risks"]))
    col_c.metric("Proximas acoes", len(report_summary["next_actions"]))

    st.caption("Gerado em: " + str(report_summary["generated_at"]))

    with st.expander("Riscos detectados"):
        if report_summary["risks"]:
            for risk in report_summary["risks"]:
                st.write("- " + str(risk))
        else:
            st.write("Nenhum risco critico detectado.")

    with st.expander("Proximas acoes recomendadas"):
        if report_summary["next_actions"]:
            for action in report_summary["next_actions"]:
                st.write("- " + str(action))
        else:
            st.write("Nenhuma acao recomendada.")

    with st.expander("Relatorio completo"):
        if report_summary["markdown"]:
            st.markdown(report_summary["markdown"])
        else:
            st.json(report.get("json", {}))
