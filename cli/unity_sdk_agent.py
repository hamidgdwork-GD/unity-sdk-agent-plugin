#!/usr/bin/env python3
import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MOBILE_NOTIFICATIONS_PACKAGE = "com.unity.mobile.notifications"
MOBILE_NOTIFICATIONS_VERSION = "2.3.2"


class AgentError(Exception):
    pass


def is_unity_project(project: Path) -> bool:
    return (
        (project / "Assets").is_dir()
        and (project / "Packages").is_dir()
        and (project / "ProjectSettings").is_dir()
    )


def load_manifest(project: Path) -> dict:
    manifest_path = project / "Packages" / "manifest.json"
    if not manifest_path.exists():
        raise AgentError(f"Missing Unity package manifest: {manifest_path}")

    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AgentError(f"Invalid JSON in {manifest_path}: {exc}") from exc


def save_manifest(project: Path, manifest: dict) -> None:
    manifest_path = project / "Packages" / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def ensure_mobile_notifications_package(project: Path) -> bool:
    manifest = load_manifest(project)
    dependencies = manifest.setdefault("dependencies", {})
    current = dependencies.get(MOBILE_NOTIFICATIONS_PACKAGE)

    if current == MOBILE_NOTIFICATIONS_VERSION:
        return False

    dependencies[MOBILE_NOTIFICATIONS_PACKAGE] = MOBILE_NOTIFICATIONS_VERSION
    save_manifest(project, manifest)
    return True


def copy_template(relative_template: str, project: Path, relative_target: str) -> bool:
    source = ROOT / "core" / "integrations" / "mobile-notifications" / "templates" / relative_template
    target = project / relative_target
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() and target.read_text(encoding="utf-8") == source.read_text(encoding="utf-8"):
        return False

    shutil.copyfile(source, target)
    return True


def validate_mobile_notifications(project: Path) -> dict:
    checks = []

    checks.append({
        "id": "unity_project",
        "passed": is_unity_project(project),
        "message": "Target folder has Unity project structure."
    })

    package_present = False
    manifest_error = None
    try:
        manifest = load_manifest(project)
        package_present = MOBILE_NOTIFICATIONS_PACKAGE in manifest.get("dependencies", {})
    except AgentError as exc:
        manifest_error = str(exc)

    checks.append({
        "id": "package_manifest",
        "passed": package_present,
        "message": (
            f"{MOBILE_NOTIFICATIONS_PACKAGE} is listed in Packages/manifest.json."
            if package_present else manifest_error or f"{MOBILE_NOTIFICATIONS_PACKAGE} is missing from Packages/manifest.json."
        )
    })

    generated_files = [
        "Assets/Scripts/Notifications/MobileNotificationService.cs",
        "Assets/Editor/IntegrationAgent/MobileNotificationTestMenu.cs",
    ]

    for relative_path in generated_files:
        checks.append({
            "id": relative_path.replace("/", "_").replace(".", "_"),
            "passed": (project / relative_path).exists(),
            "message": f"{relative_path} exists."
        })

    return {
        "integration": "mobile-notifications",
        "valid": all(check["passed"] for check in checks),
        "checks": checks,
        "manual_steps": [
            "Open the project in Unity so Package Manager can resolve the package.",
            "Test notification scheduling on a real Android device.",
            "This integration adds local notifications, not remote push notifications."
        ]
    }


def write_report(project: Path, action: str, changed_files: list[str], validation: dict) -> Path:
    reports_dir = project / "IntegrationAgentReports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_path = reports_dir / f"{action}-mobile-notifications-{timestamp}.json"
    report = {
        "action": action,
        "integration": "mobile-notifications",
        "changed_files": changed_files,
        "validation": validation,
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report_path


def add_mobile_notifications(project: Path) -> dict:
    if not is_unity_project(project):
        raise AgentError(f"Not a Unity project: {project}")

    changed_files = []

    if ensure_mobile_notifications_package(project):
        changed_files.append("Packages/manifest.json")

    template_targets = [
        ("MobileNotificationService.cs", "Assets/Scripts/Notifications/MobileNotificationService.cs"),
        ("MobileNotificationTestMenu.cs", "Assets/Editor/IntegrationAgent/MobileNotificationTestMenu.cs"),
    ]

    for template_name, target in template_targets:
        if copy_template(template_name, project, target):
            changed_files.append(target)

    validation = validate_mobile_notifications(project)
    report_path = write_report(project, "add", changed_files, validation)

    return {
        "changed_files": changed_files,
        "validation": validation,
        "report_path": str(report_path),
    }


def print_result(result: dict) -> None:
    print(json.dumps(result, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Unity SDK Agent Plugin CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a Unity SDK integration")
    add_parser.add_argument("integration", choices=["mobile-notifications"])
    add_parser.add_argument("--project", required=True, help="Path to a Unity project")

    validate_parser = subparsers.add_parser("validate", help="Validate a Unity SDK integration")
    validate_parser.add_argument("integration", choices=["mobile-notifications"])
    validate_parser.add_argument("--project", required=True, help="Path to a Unity project")

    args = parser.parse_args()
    project = Path(args.project).expanduser().resolve()

    try:
        if args.command == "add":
            result = add_mobile_notifications(project)
        else:
            validation = validate_mobile_notifications(project)
            report_path = write_report(project, "validate", [], validation)
            result = {"validation": validation, "report_path": str(report_path)}

        print_result(result)
        return 0 if result["validation"].get("valid", False) else 2
    except AgentError as exc:
        print_result({"error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
