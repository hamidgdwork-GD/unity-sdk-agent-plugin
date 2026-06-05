#!/usr/bin/env python3
import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
import re


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


def read_meta_guid(path: Path) -> str | None:
    if not path.exists():
        return None

    match = re.search(r"^guid:\s*([a-fA-F0-9]+)\s*$", path.read_text(encoding="utf-8", errors="ignore"), re.MULTILINE)
    return match.group(1) if match else None


def get_first_enabled_scene(project: Path) -> str | None:
    build_settings = project / "ProjectSettings" / "EditorBuildSettings.asset"
    if not build_settings.exists():
        return None

    content = build_settings.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(r"- enabled:\s*1\s+path:\s*(Assets/.+?\.unity)", re.MULTILINE)
    match = pattern.search(content)
    return match.group(1).strip() if match else None


def ensure_android_define_symbol(project: Path, symbol: str) -> bool:
    project_settings = project / "ProjectSettings" / "ProjectSettings.asset"
    if not project_settings.exists():
        raise AgentError(f"Missing ProjectSettings.asset: {project_settings}")

    content = project_settings.read_text(encoding="utf-8", errors="ignore")
    android_match = re.search(r"(^\s*Android:\s*)(.*)$", content, re.MULTILINE)
    if not android_match:
        raise AgentError("Could not find Android scripting define symbols in ProjectSettings.asset")

    current_symbols = [item for item in android_match.group(2).split(";") if item]
    if symbol in current_symbols:
        return False

    current_symbols.append(symbol)
    replacement = android_match.group(1) + ";".join(current_symbols)
    content = content[:android_match.start()] + replacement + content[android_match.end():]
    project_settings.write_text(content, encoding="utf-8")
    return True


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


def write_mobile_notification_settings(project: Path) -> bool:
    common_icon_guid = read_meta_guid(project / "Assets" / "GleyPlugins" / "Icons" / "commonicon.jpg.meta")
    small_icon_guid = read_meta_guid(project / "Assets" / "GleyPlugins" / "Icons" / "smallicon.png.meta")

    if not common_icon_guid or not small_icon_guid:
        raise AgentError("Missing commonicon/smallicon icon meta GUIDs under Assets/GleyPlugins/Icons")

    settings_path = project / "ProjectSettings" / "NotificationsSettings.asset"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    content = {
        "MonoBehaviour": {
            "m_Enabled": True,
            "m_EditorHideFlags": 0,
            "m_Name": "",
            "m_EditorClassIdentifier": "",
            "ToolbarIndex": 0,
            "m_iOSNotificationSettingsValues": {
                "m_Keys": [
                    "UnityNotificationRequestAuthorizationOnAppLaunch",
                    "UnityNotificationDefaultAuthorizationOptions",
                    "UnityAddRemoteNotificationCapability",
                    "UnityNotificationRequestAuthorizationForRemoteNotificationsOnAppLaunch",
                    "UnityRemoteNotificationForegroundPresentationOptions",
                    "UnityUseAPSReleaseEnvironment",
                    "UnityUseLocationNotificationTrigger",
                    "UnityAddTimeSensitiveEntitlement"
                ],
                "m_Values": ["True", "7", "False", "False", "-1", "False", "False", "False"]
            },
            "m_AndroidNotificationSettingsValues": {
                "m_Keys": [
                    "UnityNotificationAndroidRescheduleOnDeviceRestart",
                    "UnityNotificationAndroidScheduleExactAlarms",
                    "UnityNotificationAndroidUseCustomActivity",
                    "UnityNotificationAndroidCustomActivityString"
                ],
                "m_Values": ["True", "0", "False", "com.unity3d.player.UnityPlayerActivity"]
            },
            "DrawableResources": [
                {
                    "Id": "commonicon",
                    "Type": 1,
                    "Asset": {"fileID": 2800000, "guid": common_icon_guid, "type": 3}
                },
                {
                    "Id": "smallicon",
                    "Type": 0,
                    "Asset": {"fileID": 2800000, "guid": small_icon_guid, "type": 3}
                }
            ]
        }
    }
    new_text = json.dumps(content, indent=4) + "\n"
    if settings_path.exists() and settings_path.read_text(encoding="utf-8", errors="ignore") == new_text:
        return False

    settings_path.write_text(new_text, encoding="utf-8")
    return True


def place_notifications_prefab_in_scene(project: Path, scene_path: str | None = None) -> tuple[bool, str]:
    relative_scene = scene_path or get_first_enabled_scene(project)
    if not relative_scene:
        raise AgentError("Could not determine startup scene. Pass --scene or configure EditorBuildSettings.")

    scene = project / relative_scene
    if not scene.exists():
        raise AgentError(f"Scene does not exist: {scene}")

    content = scene.read_text(encoding="utf-8", errors="ignore")
    if "NotificationsManager" in content and "c73403abc2e96364e8371e2945ac8ad5" in content:
        return False, relative_scene

    ids = [int(match) for match in re.findall(r"--- !u!\d+ &(\d+)", content)]
    prefab_instance_id = (max(ids) + 1000) if ids else 520446416
    prefab_block = """
--- !u!1001 &__PREFAB_INSTANCE_ID__
PrefabInstance:
  m_ObjectHideFlags: 0
  serializedVersion: 2
  m_Modification:
    serializedVersion: 3
    m_TransformParent: {fileID: 0}
    m_Modifications:
    - target: {fileID: 40028404418495020, guid: c73403abc2e96364e8371e2945ac8ad5,
        type: 3}
      propertyPath: m_Name
      value: NotificationsManager
      objectReference: {fileID: 0}
    - target: {fileID: 2237340795062603232, guid: c73403abc2e96364e8371e2945ac8ad5,
        type: 3}
      propertyPath: m_LocalPosition.x
      value: 0
      objectReference: {fileID: 0}
    - target: {fileID: 2237340795062603232, guid: c73403abc2e96364e8371e2945ac8ad5,
        type: 3}
      propertyPath: m_LocalPosition.y
      value: 0
      objectReference: {fileID: 0}
    - target: {fileID: 2237340795062603232, guid: c73403abc2e96364e8371e2945ac8ad5,
        type: 3}
      propertyPath: m_LocalPosition.z
      value: 0
      objectReference: {fileID: 0}
    - target: {fileID: 2237340795062603232, guid: c73403abc2e96364e8371e2945ac8ad5,
        type: 3}
      propertyPath: m_LocalRotation.w
      value: 1
      objectReference: {fileID: 0}
    - target: {fileID: 5185593141163908411, guid: c73403abc2e96364e8371e2945ac8ad5,
        type: 3}
      propertyPath: initOnStart
      value: 0
      objectReference: {fileID: 0}
    - target: {fileID: 5185593141163908411, guid: c73403abc2e96364e8371e2945ac8ad5,
        type: 3}
      propertyPath: sendAnalytics
      value: 1
      objectReference: {fileID: 0}
    m_RemovedComponents: []
    m_RemovedGameObjects: []
    m_AddedGameObjects: []
    m_AddedComponents: []
  m_SourcePrefab: {fileID: 100100000, guid: c73403abc2e96364e8371e2945ac8ad5, type: 3}
""".replace("__PREFAB_INSTANCE_ID__", str(prefab_instance_id))
    scene.write_text(content.rstrip() + "\n" + prefab_block, encoding="utf-8")
    return True, relative_scene


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
        unity_configurator = project / "Assets" / "Editor" / "IntegrationAgent" / "GleyNotificationUnityConfigurator.cs"
        startup_scene = get_first_enabled_scene(project)
        startup_scene_path = project / startup_scene if startup_scene else project / "Assets" / "CodeArchitecture" / "Scenes" / "SplashScene.unity"

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
                "unity_notification_configurator",
                file_contains(unity_configurator, ["NotificationSettings.AndroidSettings.AddDrawableResource", "commonicon", "smallicon"]),
                "Unity editor configurator exists to apply Mobile Notifications icons through the package API."
            ),
            (
                "firebase_remote_config_hook",
                file_contains(firebase_script, ["Firebase.RemoteConfig", "isNotificationActive", "notificationHours", "NotificationsManager.Instance.Init()"]),
                "Firebase Remote Config hook sets notification active/hour values and initializes NotificationsManager."
            ),
            (
                "splash_scene_manager",
                file_contains(startup_scene_path, ["NotificationsManager"]),
                f"Startup scene contains a NotificationsManager object or prefab instance: {startup_scene or 'Assets/CodeArchitecture/Scenes/SplashScene.unity'}"
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
            "In Unity, run Tools > Integration Agent > Mobile Notifications > Configure Gley Notification Settings so the Mobile Notifications UI applies commonicon and smallicon.",
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


def configure_gley_notifications(project: Path, scene_path: str | None = None, write_report_file: bool = True) -> dict:
    if not is_unity_project(project):
        raise AgentError(f"Not a Unity project: {project}")

    changed_files = []

    if ensure_mobile_notifications_package(project):
        changed_files.append("Packages/manifest.json")

    if not (project / "Assets" / "GleyPlugins").exists():
        gley_result = install_vendored_gley(project)
        changed_files.extend(gley_result["changed_files"])

    if ensure_android_define_symbol(project, "EnableNotificationsAndroid"):
        changed_files.append("ProjectSettings/ProjectSettings.asset")

    if write_mobile_notification_settings(project):
        changed_files.append("ProjectSettings/NotificationsSettings.asset")

    if copy_template(
        "GleyNotificationUnityConfigurator.cs",
        project,
        "Assets/Editor/IntegrationAgent/GleyNotificationUnityConfigurator.cs"
    ):
        changed_files.append("Assets/Editor/IntegrationAgent/GleyNotificationUnityConfigurator.cs")

    placed_prefab, configured_scene = place_notifications_prefab_in_scene(project, scene_path)
    if placed_prefab:
        changed_files.append(configured_scene)

    validation = validate_mobile_notifications(project, "gley-remote-config")
    report_path = write_report(project, "configure", changed_files, validation) if write_report_file else None

    return {
        "changed_files": changed_files,
        "configured_scene": configured_scene,
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

    configure_parser = subparsers.add_parser("configure-gley-notifications", help="Configure the full Gley + Firebase notification profile")
    configure_parser.add_argument("--project", required=True, help="Path to a Unity project")
    configure_parser.add_argument("--scene", help="Startup scene path, for example Assets/Scenes/Splash.unity")
    configure_parser.add_argument("--no-report", action="store_true", help="Do not write IntegrationAgentReports output")

    args = parser.parse_args()
    project = Path(args.project).expanduser().resolve()

    try:
        if args.command == "install-gley":
            result = install_vendored_gley(project, args.force)
            print_result(result)
            return 0

        if args.command == "configure-gley-notifications":
            result = configure_gley_notifications(project, args.scene, not args.no_report)
            print_result(result)
            return 0 if result["validation"].get("valid", False) else 2

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
