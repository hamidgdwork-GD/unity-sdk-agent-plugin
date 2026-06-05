#!/usr/bin/env python3
import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MOBILE_NOTIFICATIONS_PACKAGE = "com.unity.mobile.notifications"
MOBILE_NOTIFICATIONS_VERSION = "2.4.3"
VENDORED_GLEY_PATH = ROOT / "vendor" / "gley-mobile-push-notifications" / "Assets" / "GleyPlugins"


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


def install_vendored_gley(project: Path, force: bool = False) -> dict:
    if not is_unity_project(project):
        raise AgentError(f"Not a Unity project: {project}")

    if not VENDORED_GLEY_PATH.exists():
        raise AgentError(f"Vendored Gley plugin is missing: {VENDORED_GLEY_PATH}")

    target = project / "Assets" / "GleyPlugins"
    if target.exists() and not force:
        return {
            "changed_files": [],
            "installed": False,
            "message": "Assets/GleyPlugins already exists. Use --force to overwrite it."
        }

    if target.exists() and force:
        shutil.rmtree(target)

    shutil.copytree(VENDORED_GLEY_PATH, target)
    return {
        "changed_files": ["Assets/GleyPlugins"],
        "installed": True,
        "message": "Vendored Gley plugin copied to Assets/GleyPlugins."
    }


def file_contains(path: Path, needles: list[str]) -> bool:
    if not path.exists():
        return False

    content = path.read_text(encoding="utf-8", errors="ignore")
    return all(needle in content for needle in needles)


def validate_mobile_notifications(project: Path, profile: str = "basic") -> dict:
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

    if profile == "basic":
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

    if profile == "gley-remote-config":
        project_settings = project / "ProjectSettings" / "ProjectSettings.asset"
        notification_settings = project / "ProjectSettings" / "NotificationsSettings.asset"
        firebase_script = project / "Assets" / "Scripts" / "firebasecall.cs"
        gley_facade = project / "Assets" / "GleyPlugins" / "Notifications" / "Scripts" / "GleyNotifications.cs"
        gley_runtime = project / "Assets" / "GleyPlugins" / "Notifications" / "Scripts" / "NotificationManager.cs"
        gley_manager = project / "Assets" / "GleyPlugins" / "Implementation" / "NotificationsManager.cs"
        gley_prefab = project / "Assets" / "GleyPlugins" / "Implementation" / "NotificationsManager.prefab"
        gley_settings = project / "Assets" / "GleyPlugins" / "Notifications" / "Resources" / "NotificationSettingsData.asset"
        splash_scene = project / "Assets" / "CodeArchitecture" / "Scenes" / "SplashScene.unity"

        profile_checks = [
            (
                "android_define_symbol",
                file_contains(project_settings, ["EnableNotificationsAndroid"]),
                "ProjectSettings.asset contains Android define symbol EnableNotificationsAndroid."
            ),
            (
                "notification_icons",
                file_contains(notification_settings, ["commonicon", "smallicon"]),
                "NotificationsSettings.asset contains commonicon and smallicon drawable resources."
            ),
            (
                "gley_facade",
                gley_facade.exists(),
                "GleyNotifications facade exists."
            ),
            (
                "gley_runtime_manager",
                file_contains(gley_runtime, ["EnableNotificationsAndroid", "AndroidNotificationCenter", "SendNotificationWithExplicitID"]),
                "Gley runtime NotificationManager uses Unity Mobile Notifications behind EnableNotificationsAndroid."
            ),
            (
                "game_notifications_manager",
                file_contains(gley_manager, ["isNotificationActive", "notificationHours", "ReqNotifyStatus", "OnApplicationFocus", "GleyNotifications.SendNotificationOnId"]),
                "Project NotificationsManager contains remote-config flags, permission gate, focus lifecycle, and Gley scheduling."
            ),
            (
                "notifications_prefab",
                file_contains(gley_prefab, ["m_Name: NotificationsManager", "commonicon", "smallicon", "OpenFromNotification_NewDay"]),
                "NotificationsManager prefab exists with serialized icon IDs and New Day notification data."
            ),
            (
                "gley_settings_android",
                file_contains(gley_settings, ["useForAndroid: 1"]),
                "Gley NotificationSettingsData is enabled for Android."
            ),
            (
                "firebase_remote_config_hook",
                file_contains(firebase_script, ["Firebase.RemoteConfig", "isNotificationActive", "notificationHours", "NotificationsManager.Instance.Init()"]),
                "Firebase Remote Config hook sets notification active/hour values and initializes NotificationsManager."
            ),
            (
                "splash_scene_manager",
                file_contains(splash_scene, ["NotificationsManager"]),
                "SplashScene contains a NotificationsManager object or prefab instance."
            ),
        ]

        for check_id, passed, message in profile_checks:
            checks.append({
                "id": check_id,
                "passed": passed,
                "message": message
            })

    return {
        "integration": "mobile-notifications",
        "profile": profile,
        "valid": all(check["passed"] for check in checks),
        "checks": checks,
        "manual_steps": [
            "Open the project in Unity so Package Manager can resolve the package.",
            "Test notification scheduling on a real Android device.",
            "This integration adds local notifications, not remote push notifications.",
            "For the gley-remote-config profile, configure Firebase Remote Config keys: isNotificationActive and notificationHours."
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


def add_mobile_notifications(project: Path, profile: str = "basic", write_report_file: bool = True) -> dict:
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

    validation = validate_mobile_notifications(project, profile)
    report_path = write_report(project, "add", changed_files, validation) if write_report_file else None

    return {
        "changed_files": changed_files,
        "validation": validation,
        "report_path": str(report_path) if report_path else None,
    }


def print_result(result: dict) -> None:
    print(json.dumps(result, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Unity SDK Agent Plugin CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a Unity SDK integration")
    add_parser.add_argument("integration", choices=["mobile-notifications"])
    add_parser.add_argument("--project", required=True, help="Path to a Unity project")
    add_parser.add_argument("--profile", choices=["basic", "gley-remote-config"], default="basic")
    add_parser.add_argument("--no-report", action="store_true", help="Do not write IntegrationAgentReports output")

    validate_parser = subparsers.add_parser("validate", help="Validate a Unity SDK integration")
    validate_parser.add_argument("integration", choices=["mobile-notifications"])
    validate_parser.add_argument("--project", required=True, help="Path to a Unity project")
    validate_parser.add_argument("--profile", choices=["basic", "gley-remote-config"], default="basic")
    validate_parser.add_argument("--no-report", action="store_true", help="Do not write IntegrationAgentReports output")

    gley_parser = subparsers.add_parser("install-gley", help="Install the vendored Gley plugin into a Unity project")
    gley_parser.add_argument("--project", required=True, help="Path to a Unity project")
    gley_parser.add_argument("--force", action="store_true", help="Overwrite existing Assets/GleyPlugins")

    args = parser.parse_args()
    project = Path(args.project).expanduser().resolve()

    try:
        if args.command == "install-gley":
            result = install_vendored_gley(project, args.force)
            print_result(result)
            return 0

        if args.command == "add":
            result = add_mobile_notifications(project, args.profile, not args.no_report)
        else:
            validation = validate_mobile_notifications(project, args.profile)
            report_path = write_report(project, "validate", [], validation) if not args.no_report else None
            result = {"validation": validation, "report_path": str(report_path) if report_path else None}

        print_result(result)
        return 0 if result["validation"].get("valid", False) else 2
    except AgentError as exc:
        print_result({"error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
