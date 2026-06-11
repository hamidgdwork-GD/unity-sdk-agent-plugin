# Unity SDK Agent Plugin Instructions

Use this repository as an agent toolkit for Unity SDK integrations.

When a user asks to add, fix, configure, or validate Unity mobile notifications, do not guess the setup and do not stop after copying packages. Follow the production workflow below.

## Mobile Notifications Production Workflow

Target integration:

```text
mobile-notifications
```

Required profile:

```text
gley-remote-config
```

Run the full configurator:

```powershell
python cli/unity_sdk_agent.py configure-gley-notifications --project "<UnityProjectPath>"
```

This command is responsible for:

- installing `com.unity.mobile.notifications` version `2.4.3`
- copying bundled Gley if `Assets/GleyPlugins` is missing
- adding Android define symbol `EnableNotificationsAndroid`
- generating `Assets/Editor/IntegrationAgent/GleyNotificationUnityConfigurator.cs`
- staging the Unity-side configurator that applies Mobile Notification settings
- staging the Unity-side configurator that places `NotificationsManager` in the first enabled build scene
- writing a validation report

Safety rule: the CLI must not directly edit `.unity` scene YAML and must not directly write `ProjectSettings/NotificationsSettings.asset`. Those files are Unity-owned and must be changed by the generated Unity Editor configurator.

## Required Unity Editor Step

After running `configure-gley-notifications`, the agent must ensure this Unity Editor method is executed:

```text
IntegrationAgent.Editor.GleyNotificationUnityConfigurator.ConfigureForBatchmode
```

Preferred if Unity executable is available:

```powershell
"<Unity.exe>" -batchmode -quit -projectPath "<UnityProjectPath>" -executeMethod IntegrationAgent.Editor.GleyNotificationUnityConfigurator.ConfigureForBatchmode
```

If the agent cannot run Unity batchmode, it must clearly report this remaining user action:

```text
Open Unity and run:
Tools > Integration Agent > Mobile Notifications > Configure Gley Notification Settings
```

This step is not optional. It uses Unity's official Mobile Notifications editor API to make `commonicon` and `smallicon` appear in Project Settings.
It also opens the first enabled build scene through `EditorSceneManager`, instantiates `Assets/GleyPlugins/Implementation/NotificationsManager.prefab` through `PrefabUtility`, sets `initOnStart = false` and `sendAnalytics = true`, then saves the scene through Unity.
When it succeeds, it writes `IntegrationAgentReports/gley-notifications-unity-configurator-status.json`. Validation must not be considered complete unless this report exists.

## Validation

After configuration and the Unity Editor step, run:

```powershell
python cli/unity_sdk_agent.py validate mobile-notifications --profile gley-remote-config --no-report --project "<UnityProjectPath>"
```

The integration is incomplete if validation fails or if Unity Project Settings > Mobile Notifications shows an empty notification icon list.
The integration is also incomplete if `unity_configurator_executed` fails, because that means the Unity-side setup did not run.

## Do Not

- Do not run only `install-gley` and call the task done.
- Do not run only `add mobile-notifications` for production projects.
- Do not rely only on manual JSON edits to `ProjectSettings/NotificationsSettings.asset`.
- Do not manually append prefab YAML to `.unity` scene files. This can corrupt the startup/splash scene.
- Do not overwrite an existing `Assets/GleyPlugins` with `--force` unless the user explicitly approves.
- Do not ask for approval just because `Assets/GleyPlugins` is missing. The owner-approved bundled Gley copy is part of the production setup and should be installed automatically by `configure-gley-notifications`.
- Do not claim the integration is complete until validation passes and the Unity-side icon configurator has been executed or explicitly reported as pending.
