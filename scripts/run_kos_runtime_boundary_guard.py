
from pathlib import Path
from datetime import datetime
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ARCHIVES = ROOT / "local_runtime" / "kos_archives"
ARCHIVES.mkdir(parents=True, exist_ok=True)

VOLATILE = {
    "campaigns/hupmix_gp_recovery/GP_VIDEO_02_REAL_PRODUCTION_BRIEF.json",
    "campaigns/hupmix_gp_recovery/GP_VIDEO_02_CAPTURE_MISSION.json",
    "campaigns/hupmix_gp_recovery/GP_VIDEO_02_CAPTURE_MISSION.md",
    "reports/KOS_CAPABILITY_EXECUTOR_LAST_RUN.json",
    "reports/KOS_CAPABILITY_EXECUTOR_V1.json",
    "reports/KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_AUDIT.json",
    "reports/KOS_HUPMIX_GP_VIDEO_02_REAL_ASSET_AUDIT.md",
    "reports/KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.json",
    "reports/KOS_HUPMIX_INSTAGRAM_CONTINUITY_AUDIT.md",
    "reports/KOS_HUPMIX_GP_VIDEO_02_CAPTURE_MISSION_V1.json",
    "reports/KOS_HUPMIX_GP_VIDEO_02_CAPTURE_MISSION_V1.md",
}

def git(args):
    return subprocess.run(["git"] + args, cwd=str(ROOT), capture_output=True, text=True, timeout=60)

def main():
    status = git(["--no-pager", "status", "--short"]).stdout.splitlines()
    bad = []
    volatile_found = []

    for line in status:
        path = line[3:].strip().replace("\\", "/")
        if path in VOLATILE:
            volatile_found.append(path)
        else:
            bad.append(line)

    report = {
        "status": "KOS_RUNTIME_BOUNDARY_CLEAN" if not status else "KOS_RUNTIME_BOUNDARY_DIRTY",
        "created_at": datetime.now().isoformat(),
        "volatile_found": volatile_found,
        "bad": bad,
        "fixed": False,
    }

    if bad:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        raise SystemExit(2)

    if volatile_found:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive = ARCHIVES / f"runtime_boundary_guard_{stamp}"
        archive.mkdir(parents=True, exist_ok=True)

        for p in volatile_found:
            src = ROOT / p
            if src.exists():
                shutil.copy2(src, archive / src.name)

        git(["restore", "--"] + volatile_found)
        report["fixed"] = True
        report["archive"] = str(archive.relative_to(ROOT)).replace("\\", "/")
        report["status"] = "KOS_RUNTIME_BOUNDARY_FIXED"

    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
