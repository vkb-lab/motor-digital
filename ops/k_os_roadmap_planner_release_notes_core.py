# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

POLICY_PATH = ROOT / "config" / "roadmap" / "k_os_roadmap_release_policy.json"
ROADMAP_DIR = ROOT / "local_secrets" / "k_os_roadmap"
ROADMAP_PATH = ROADMAP_DIR / "roadmap_release_registry.json"

REPORT_DIR = ROOT / "reports" / "roadmap"
MEMORY_DIR = ROOT / "memory" / "roadmap"

LATEST_JSON = REPORT_DIR / "latest_roadmap_release_report.json"
LATEST_MD = REPORT_DIR / "latest_roadmap_release_report.md"
ROADMAP_JSON = REPORT_DIR / "latest_internal_roadmap_snapshot.json"
ROADMAP_MD = REPORT_DIR / "latest_internal_roadmap_snapshot.md"
NOTES_JSON = REPORT_DIR / "latest_release_notes_draft.json"
NOTES_MD = REPORT_DIR / "latest_release_notes_draft.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

PRODUCT_FEEDBACK_REPORT = ROOT / "reports" / "product_feedback" / "latest_product_feedback_report.json"
PRODUCT_BACKLOG_REPORT = ROOT / "reports" / "product_feedback" / "latest_product_backlog_snapshot.json"
ROADMAP_CANDIDATE_REPORT = ROOT / "reports" / "product_feedback" / "latest_roadmap_candidate_snapshot.json"


def now_dt() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def now() -> str:
    return now_dt().isoformat()


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"_read_error": str(exc), "_path": str(path)}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def event(name: str, data: dict[str, Any]) -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with EVENTS_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps({
            "event": name,
            "created_at": now(),
            "data": data
        }, ensure_ascii=False) + "\n")


def load_policy() -> dict[str, Any]:
    data = read_json(POLICY_PATH)
    if not data:
        raise RuntimeError("Roadmap policy not found.")
    return data


def ensure_registry() -> dict[str, Any]:
    ROADMAP_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not ROADMAP_PATH.exists():
        data = {
            "version": "1.0.0",
            "created_at": now(),
            "updated_at": now(),
            "local_only": True,
            "external_publish_enabled": False,
            "automatic_release_publish_enabled": False,
            "releases": [],
            "release_feature_links": [],
            "release_notes": [],
            "activities": []
        }
        write_json(ROADMAP_PATH, data)

    registry = read_json(ROADMAP_PATH)
    if not registry:
        raise RuntimeError("Could not load roadmap registry.")
    return registry


def save_registry(data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    write_json(ROADMAP_PATH, data)


def load_product_features() -> list[dict[str, Any]]:
    data = read_json(PRODUCT_FEEDBACK_REPORT) or {}
    return data.get("feature_requests", [])


def load_roadmap_candidates() -> list[dict[str, Any]]:
    data = read_json(ROADMAP_CANDIDATE_REPORT) or {}
    candidates = data.get("candidates", [])
    if candidates:
        return candidates
    return load_product_features()


def safe_release(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "release_id": item.get("release_id"),
        "title": item.get("title"),
        "version_label": item.get("version_label"),
        "release_type": item.get("release_type"),
        "channel": item.get("channel"),
        "status": item.get("status"),
        "target_date": item.get("target_date", ""),
        "owner": item.get("owner"),
        "linked_feature_count": len(item.get("linked_feature_ids", [])),
        "linked_feature_ids": item.get("linked_feature_ids", []),
        "public_release_notes_allowed": item.get("public_release_notes_allowed", False),
        "external_publish_performed": item.get("external_publish_performed", False),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at", "")
    }


def safe_link(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "link_id": item.get("link_id"),
        "release_id": item.get("release_id"),
        "feature_id": item.get("feature_id"),
        "feature_title": item.get("feature_title", ""),
        "feature_status": item.get("feature_status"),
        "reason": item.get("reason"),
        "created_at": item.get("created_at")
    }


def safe_notes(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "release_notes_id": item.get("release_notes_id"),
        "release_id": item.get("release_id"),
        "audience": item.get("audience"),
        "status": item.get("status"),
        "requires_approval_before_publish": item.get("requires_approval_before_publish", True),
        "external_publish_performed": item.get("external_publish_performed", False),
        "created_at": item.get("created_at")
    }


def safe_activity(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "activity_id": item.get("activity_id"),
        "activity_type": item.get("activity_type"),
        "summary": item.get("summary"),
        "created_at": item.get("created_at"),
        "created_by": item.get("created_by")
    }


def find_feature(feature_id: str) -> dict[str, Any] | None:
    for feature in load_product_features():
        if feature.get("feature_id") == feature_id:
            return feature
    return None


def create_release(title: str, version_label: str, release_type: str, channel: str, target_date: str, owner: str) -> dict[str, Any]:
    policy = load_policy()

    if release_type not in set(policy.get("release_types", [])):
        raise RuntimeError(f"Invalid release type: {release_type}")

    if channel not in set(policy.get("release_channels", [])):
        raise RuntimeError(f"Invalid release channel: {channel}")

    registry = ensure_registry()
    release_id = "rel_" + uuid.uuid4().hex[:12]

    release = {
        "release_id": release_id,
        "title": title,
        "version_label": version_label,
        "release_type": release_type,
        "channel": channel,
        "status": "draft",
        "target_date": target_date or (now_dt() + timedelta(days=14)).date().isoformat(),
        "owner": owner or "k_os_operator",
        "linked_feature_ids": [],
        "public_release_notes_allowed": False,
        "customer_facing_roadmap_allowed": False,
        "external_publish_performed": False,
        "created_at": now(),
        "updated_at": now()
    }

    registry["releases"].append(release)
    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "activity_type": "release_created",
        "summary": f"Release criada: {title} / {version_label}.",
        "created_at": now(),
        "created_by": owner or "k_os_operator"
    })

    save_registry(registry)
    event("roadmap.release_created", {"release_id": release_id, "version_label": version_label})
    return audit_report()


def add_feature_to_release(release_id: str, feature_id: str, reason: str) -> dict[str, Any]:
    registry = ensure_registry()
    release = next((item for item in registry.get("releases", []) if item.get("release_id") == release_id), None)

    if not release:
        raise RuntimeError(f"Release not found: {release_id}")

    feature = find_feature(feature_id)
    if not feature:
        raise RuntimeError(f"Feature not found in product feedback report: {feature_id}")

    link_id = "rfl_" + uuid.uuid4().hex[:12]

    registry["release_feature_links"].append({
        "link_id": link_id,
        "release_id": release_id,
        "feature_id": feature_id,
        "feature_title": feature.get("title", ""),
        "feature_status": "candidate",
        "reason": reason or "manual_release_planning",
        "created_at": now()
    })

    linked = set(release.get("linked_feature_ids", []))
    linked.add(feature_id)
    release["linked_feature_ids"] = sorted(linked)
    release["updated_at"] = now()

    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "activity_type": "feature_added_to_release",
        "summary": f"Feature {feature_id} vinculada a release {release_id}.",
        "created_at": now(),
        "created_by": "operator"
    })

    save_registry(registry)
    event("roadmap.feature_added_to_release", {"release_id": release_id, "feature_id": feature_id})
    return audit_report()


def set_release_status(release_id: str, status: str, reason: str) -> dict[str, Any]:
    policy = load_policy()

    if status not in set(policy.get("release_statuses", [])):
        raise RuntimeError(f"Invalid release status: {status}")

    registry = ensure_registry()
    release = next((item for item in registry.get("releases", []) if item.get("release_id") == release_id), None)

    if not release:
        raise RuntimeError(f"Release not found: {release_id}")

    if status in {"approved_for_manual_publish", "published_manually"}:
        if "approval" not in (reason or "").lower() and "review" not in (reason or "").lower():
            raise RuntimeError("Public/publish status requires explicit approval or review reason.")

    if status == "published_manually":
        release["external_publish_performed"] = False
        release["manual_publish_recorded"] = True

    release["status"] = status
    release["last_status_reason"] = reason or "manual_update"
    release["updated_at"] = now()

    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "activity_type": "release_status_changed",
        "summary": f"Release {release_id} alterada para {status}.",
        "created_at": now(),
        "created_by": "operator"
    })

    save_registry(registry)
    event("roadmap.release_status_changed", {"release_id": release_id, "status": status})
    return audit_report()


def create_demo() -> dict[str, Any]:
    registry = ensure_registry()

    if not registry.get("releases"):
        release_id = "rel_" + uuid.uuid4().hex[:12]
        registry["releases"].append({
            "release_id": release_id,
            "title": "K-OS SaaS Evolution Release",
            "version_label": "v0.35-internal",
            "release_type": "minor",
            "channel": "internal",
            "status": "draft",
            "target_date": (now_dt() + timedelta(days=14)).date().isoformat(),
            "owner": "k_os_operator",
            "linked_feature_ids": [],
            "public_release_notes_allowed": False,
            "customer_facing_roadmap_allowed": False,
            "external_publish_performed": False,
            "created_at": now(),
            "updated_at": now()
        })

    candidates = load_roadmap_candidates()
    registry = ensure_registry()

    if registry.get("releases") and candidates and not registry.get("release_feature_links"):
        release = registry["releases"][0]
        feature = candidates[0]
        feature_id = feature.get("feature_id", "")

        if feature_id:
            registry["release_feature_links"].append({
                "link_id": "rfl_" + uuid.uuid4().hex[:12],
                "release_id": release["release_id"],
                "feature_id": feature_id,
                "feature_title": feature.get("title", ""),
                "feature_status": "candidate",
                "reason": "demo_top_roadmap_candidate",
                "created_at": now()
            })
            release["linked_feature_ids"] = [feature_id]
            release["updated_at"] = now()

    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "activity_type": "demo_created",
        "summary": "Demo de roadmap criada localmente.",
        "created_at": now(),
        "created_by": "k_os_roadmap_planner"
    })

    save_registry(registry)

    if registry.get("releases"):
        generate_release_notes(registry["releases"][0]["release_id"], "internal")

    event("roadmap.demo_created", {"ok": True})
    return audit_report()


def linked_features_for_release(registry: dict[str, Any], release_id: str) -> list[dict[str, Any]]:
    links = [item for item in registry.get("release_feature_links", []) if item.get("release_id") == release_id]
    features = load_product_features()
    result = []

    for link in links:
        feature = next((item for item in features if item.get("feature_id") == link.get("feature_id")), None)
        if feature:
            result.append(feature)
        else:
            result.append({
                "feature_id": link.get("feature_id"),
                "title": link.get("feature_title", ""),
                "category": "unknown",
                "priority": "unknown",
                "impact_score": 0,
                "status": "unknown"
            })

    return result


def generate_release_notes(release_id: str, audience: str) -> dict[str, Any]:
    registry = ensure_registry()
    release = next((item for item in registry.get("releases", []) if item.get("release_id") == release_id), None)

    if not release:
        raise RuntimeError(f"Release not found: {release_id}")

    if audience not in {"internal", "public_draft"}:
        raise RuntimeError("Audience must be internal or public_draft.")

    features = linked_features_for_release(registry, release_id)
    notes_id = "rn_" + uuid.uuid4().hex[:12]

    status = "draft"
    requires_approval = True

    content_lines = [
        f"# Release Notes - {release.get('version_label')}",
        "",
        f"Release: {release.get('title')}",
        f"Canal: {release.get('channel')}",
        f"Tipo: {release.get('release_type')}",
        f"Audience: {audience}",
        "",
        "Aviso: rascunho interno. Publicação externa exige aprovação humana.",
        "",
        "## Features incluídas",
        ""
    ]

    if features:
        for feature in features:
            content_lines.append(
                f"- {feature.get('title')} | categoria={feature.get('category')} | "
                f"prioridade={feature.get('priority')} | score={feature.get('impact_score')}"
            )
    else:
        content_lines.append("- Nenhuma feature vinculada.")

    content_lines.extend([
        "",
        "## Gates antes de uso público",
        "",
        "- revisão do Product Owner",
        "- revisão de QA ou operador",
        "- revisão comercial se customer-facing",
        "- revisão de segurança se aplicável",
        "- revisão jurídica se aplicável",
        "- aprovação humana registrada",
        "",
        "## Bloqueios",
        "",
        "- não publicar automaticamente",
        "- não prometer roadmap externamente",
        "- não declarar feature entregue sem evidência",
        "- não expor feedback bruto de cliente"
    ])

    content = "\n".join(content_lines)

    notes = {
        "release_notes_id": notes_id,
        "release_id": release_id,
        "audience": audience,
        "status": status,
        "content": content,
        "requires_approval_before_publish": requires_approval,
        "external_publish_performed": False,
        "created_at": now()
    }

    registry["release_notes"].append(notes)
    registry["activities"].append({
        "activity_id": "act_" + uuid.uuid4().hex[:12],
        "activity_type": "release_notes_generated",
        "summary": f"Release notes geradas para {release_id} / {audience}.",
        "created_at": now(),
        "created_by": "k_os_roadmap_planner"
    })

    save_registry(registry)

    draft = {
        "ok": True,
        "checkpoint": "035",
        "module": "k_os_roadmap_planner_release_notes_core",
        "status": "release_notes_draft_generated",
        "generated_at": now(),
        "release_notes": safe_notes(notes),
        "release": safe_release(release),
        "features": features,
        "content": content,
        "external_publish_enabled": False,
        "external_publish_performed": False,
        "requires_approval_before_publish": True,
        "manual_approval_required": True,
        "next_checkpoint": "036 - K-Analytics and Executive Metrics Core"
    }

    NOTES_JSON.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
    NOTES_MD.write_text(content, encoding="utf-8")

    event("roadmap.release_notes_generated", {"release_id": release_id, "audience": audience})
    return draft


def compute_metrics(releases: list[dict[str, Any]], links: list[dict[str, Any]], notes: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    channel_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}

    for release in releases:
        status = release.get("status", "unknown")
        channel = release.get("channel", "unknown")
        release_type = release.get("release_type", "unknown")

        status_counts[status] = status_counts.get(status, 0) + 1
        channel_counts[channel] = channel_counts.get(channel, 0) + 1
        type_counts[release_type] = type_counts.get(release_type, 0) + 1

    public_sensitive_count = sum(1 for release in releases if release.get("channel") in {"customer_pilot", "public"})

    return {
        "release_count": len(releases),
        "release_feature_link_count": len(links),
        "release_notes_count": len(notes),
        "public_sensitive_release_count": public_sensitive_count,
        "status_counts": status_counts,
        "channel_counts": channel_counts,
        "type_counts": type_counts
    }


def internal_roadmap_snapshot(report: dict[str, Any]) -> dict[str, Any]:
    releases = report.get("releases", [])
    links = report.get("release_feature_links", [])

    active_statuses = {"draft", "internal_review", "planned", "in_progress", "qa_review", "ready_internal"}
    active = [item for item in releases if item.get("status") in active_statuses]

    snapshot = {
        "ok": True,
        "checkpoint": "035",
        "module": "k_os_roadmap_planner_release_notes_core",
        "status": "internal_roadmap_snapshot",
        "generated_at": now(),
        "active_release_count": len(active),
        "active_releases": active,
        "release_feature_links": links,
        "customer_facing_roadmap_allowed": False,
        "automatic_roadmap_commitment_enabled": False,
        "external_publish_enabled": False,
        "next_checkpoint": report.get("next_checkpoint")
    }

    ROADMAP_JSON.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Internal Roadmap Snapshot",
        "",
        f"- Generated at: {snapshot.get('generated_at')}",
        f"- Active releases: {snapshot.get('active_release_count')}",
        f"- Customer-facing roadmap allowed: {snapshot.get('customer_facing_roadmap_allowed')}",
        f"- External publish enabled: {snapshot.get('external_publish_enabled')}",
        "",
        "## Active releases",
        ""
    ]

    if active:
        for item in active:
            lines.append(
                f"- {item.get('release_id')} | {item.get('version_label')} | {item.get('title')} | "
                f"status={item.get('status')} | channel={item.get('channel')} | target={item.get('target_date')}"
            )
    else:
        lines.append("- Nenhuma release ativa.")

    lines.extend(["", "## Feature links", ""])

    if links:
        for item in links:
            lines.append(f"- release={item.get('release_id')} | feature={item.get('feature_id')} | {item.get('feature_title')}")
    else:
        lines.append("- Nenhuma feature vinculada a release.")

    ROADMAP_MD.write_text("\n".join(lines), encoding="utf-8")
    return snapshot


def audit_report() -> dict[str, Any]:
    registry = ensure_registry()
    policy = load_policy()

    releases = [safe_release(item) for item in registry.get("releases", [])]
    links = [safe_link(item) for item in registry.get("release_feature_links", [])]
    notes = [safe_notes(item) for item in registry.get("release_notes", [])]
    activities = [safe_activity(item) for item in registry.get("activities", [])[-30:]]

    metrics = compute_metrics(releases, links, notes)

    report = {
        "ok": True,
        "checkpoint": "035",
        "module": "k_os_roadmap_planner_release_notes_core",
        "status": "audit_generated",
        "generated_at": now(),
        "roadmap_registry_path": "local_secrets/k_os_roadmap/roadmap_release_registry.json",
        "roadmap_registry_committed": False,
        "sanitized_reports_only": True,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "automatic_message_enabled": False,
        "automatic_release_publish_enabled": False,
        "automatic_roadmap_commitment_enabled": False,
        "releases": releases,
        "release_feature_links": links,
        "release_notes": notes,
        "recent_activities": activities,
        "metrics": metrics,
        "required_gates_before_public_release": policy.get("required_gates_before_public_release", []),
        "blocked_actions": policy.get("blocked_actions", []),
        "next_checkpoint": policy.get("next_checkpoint", "036 - K-Analytics and Executive Metrics Core")
    }

    write_report(report)
    internal_roadmap_snapshot(report)
    event("roadmap.audit_generated", {"release_count": metrics["release_count"]})
    return report


def write_report(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# K-OS Roadmap Planner and Release Notes Core",
        "",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Registry committed: {report.get('roadmap_registry_committed')}",
        f"- External publish enabled: {report.get('external_publish_enabled')}",
        f"- Automatic release publish: {report.get('automatic_release_publish_enabled')}",
        f"- Automatic roadmap commitment: {report.get('automatic_roadmap_commitment_enabled')}",
        "",
        "## Metrics",
        ""
    ]

    for key, value in report.get("metrics", {}).items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Releases", ""])

    if report.get("releases"):
        for item in report.get("releases", []):
            lines.append(
                f"- {item.get('release_id')} | {item.get('version_label')} | {item.get('title')} | "
                f"{item.get('status')} | channel={item.get('channel')} | features={item.get('linked_feature_count')}"
            )
    else:
        lines.append("- Nenhuma release registrada.")

    lines.extend(["", "## Release notes", ""])

    if report.get("release_notes"):
        for item in report.get("release_notes", []):
            lines.append(
                f"- {item.get('release_notes_id')} | release={item.get('release_id')} | "
                f"audience={item.get('audience')} | approval={item.get('requires_approval_before_publish')}"
            )
    else:
        lines.append("- Nenhuma nota de release registrada.")

    lines.extend(["", "## Required gates before public release", ""])

    for gate in report.get("required_gates_before_public_release", []):
        lines.append(f"- {gate}")

    lines.extend(["", "## Blocked actions", ""])

    for action in report.get("blocked_actions", []):
        lines.append(f"- {action}")

    lines.extend(["", "## Next checkpoint", "", f"- {report.get('next_checkpoint')}"])

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")


def show_latest() -> int:
    if LATEST_JSON.exists():
        print(LATEST_JSON.read_text(encoding="utf-8-sig"))
    else:
        print("{}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["init", "create-demo", "create-release", "add-feature", "set-release-status", "generate-release-notes", "audit", "show"], required=True)
    parser.add_argument("--title", default="")
    parser.add_argument("--version-label", default="")
    parser.add_argument("--release-type", default="minor")
    parser.add_argument("--channel", default="internal")
    parser.add_argument("--target-date", default="")
    parser.add_argument("--owner", default="k_os_operator")
    parser.add_argument("--release-id", default="")
    parser.add_argument("--feature-id", default="")
    parser.add_argument("--status", default="")
    parser.add_argument("--reason", default="")
    parser.add_argument("--audience", default="internal")
    args = parser.parse_args()

    if args.mode == "init":
        ensure_registry()
        result = audit_report()

    elif args.mode == "create-demo":
        result = create_demo()

    elif args.mode == "create-release":
        if not args.title:
            raise SystemExit("Informe --title")
        if not args.version_label:
            raise SystemExit("Informe --version-label")
        result = create_release(args.title, args.version_label, args.release_type, args.channel, args.target_date, args.owner)

    elif args.mode == "add-feature":
        if not args.release_id:
            raise SystemExit("Informe --release-id")
        if not args.feature_id:
            raise SystemExit("Informe --feature-id")
        result = add_feature_to_release(args.release_id, args.feature_id, args.reason)

    elif args.mode == "set-release-status":
        if not args.release_id:
            raise SystemExit("Informe --release-id")
        if not args.status:
            raise SystemExit("Informe --status")
        result = set_release_status(args.release_id, args.status, args.reason)

    elif args.mode == "generate-release-notes":
        if not args.release_id:
            raise SystemExit("Informe --release-id")
        result = generate_release_notes(args.release_id, args.audience)

    elif args.mode == "audit":
        result = audit_report()

    elif args.mode == "show":
        return show_latest()

    else:
        raise SystemExit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())