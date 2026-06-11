# Unity SDK Integration

Use this skill when a user asks to add, validate, or explain Unity SDK integrations.

Read the root `AGENTS.md` first. It contains the canonical workflow for mobile notifications.

## Rules

- Always inspect the Unity project before modifying files.
- Prefer the CLI tool in `cli/unity_sdk_agent.py` for supported integrations.
- Do not invent SDK steps when a recipe exists.
- Gley Mobile Push Notifications is vendored under `vendor/gley-mobile-push-notifications` with owner approval.
- If Gley is required and missing from the target project, the production configurator should copy the owner-approved vendored `Assets/GleyPlugins` folder automatically. Do not stop to ask for approval unless an existing `Assets/GleyPlugins` folder would be overwritten.
- Read the selected recipe before running an integration.
- Validate after applying an integration.
- Report changed files, validation status, and manual steps.
- Ask before destructive actions. This plugin does not delete project files.
- Never manually edit `.unity` scene YAML or directly write `ProjectSettings/NotificationsSettings.asset` for this integration. The generated Unity Editor configurator must make those Unity-owned changes.

## Supported Integrations

- `mobile-notifications`: Adds Unity's official Mobile Notifications package, generates a service wrapper, generates an editor test menu, and validates the setup.
- `mobile-notifications --profile gley-remote-config`: Validates a Gley Mobile Push Notifications + Firebase Remote Config production setup.

## Standard Flow

1. Confirm the target path is a Unity project.
2. Read `core/integrations/<integration-id>/recipe.md`.
3. For `mobile-notifications`, run the production configurator:

```powershell
python cli/unity_sdk_agent.py configure-gley-notifications --project "<UnityProjectPath>"
```

4. If Unity is closed, run the editor configurator using batchmode. If Unity is already open, wait for the generated auto-run request to execute inside the open editor.
5. Validate with `--profile gley-remote-config --no-report`.
6. If validation fails, inspect the failed checks and only fix issues related to the integration.

If the project is already open in Unity, do not keep retrying batchmode. The CLI writes `IntegrationAgentReports/gley-notifications-auto-run-request.json`, and the generated editor script auto-runs inside the open editor after scripts reload. Wait for `IntegrationAgentReports/gley-notifications-unity-configurator-status.json`, then validate.

## Mobile Notifications Example

```powershell
python cli/unity_sdk_agent.py configure-gley-notifications --project "D:\Projects\MyUnityGame"
```

This is the full setup command. Do not use `add mobile-notifications` for production Gley/Firebase projects. Do not stop after `install-gley`; that only copies the plugin files.

After running `configure-gley-notifications`, the target Unity project contains:

```text
Assets/Editor/IntegrationAgent/GleyNotificationUnityConfigurator.cs
```

Tell the user to open Unity and run:

```text
Tools > Integration Agent > Mobile Notifications > Configure Gley Notification Settings
```

If Unity batchmode is available, run:

```text
-executeMethod IntegrationAgent.Editor.GleyNotificationUnityConfigurator.ConfigureForBatchmode
```

Then validate again. The Mobile Notifications Project Settings UI should show `commonicon` and `smallicon`, and the first enabled build scene should contain `NotificationsManager`.

Validation only:

```powershell
python cli/unity_sdk_agent.py validate mobile-notifications --project "D:\Projects\MyUnityGame"
```

Gley + Firebase Remote Config validation:

```powershell
python cli/unity_sdk_agent.py validate mobile-notifications --profile gley-remote-config --project "D:\Projects\MyUnityGame"
```

Use `--no-report` if the user asks to inspect without modifying the project.

Install bundled Gley plugin:

```powershell
python cli/unity_sdk_agent.py install-gley --project "D:\Projects\MyUnityGame"
```

Do not use `--force` unless the user explicitly approves overwriting an existing `Assets/GleyPlugins` folder.
