# Unity SDK Agent Plugin

Read the root `AGENTS.md` first.

For Unity mobile notifications, use the full production workflow:

```powershell
python cli/unity_sdk_agent.py configure-gley-notifications --project "<UnityProjectPath>"
```

Then run the Unity-side configurator if possible:

```text
IntegrationAgent.Editor.GleyNotificationUnityConfigurator.ConfigureForBatchmode
```

This Unity-side step configures notification icons and places `NotificationsManager` in the first enabled build scene. Do not manually edit `.unity` scene YAML or directly write `ProjectSettings/NotificationsSettings.asset`.

If the project is already open in Unity, do not retry batchmode. Wait for the generated editor script to consume `IntegrationAgentReports/gley-notifications-auto-run-request.json` and create `IntegrationAgentReports/gley-notifications-unity-configurator-status.json`.

Then validate:

```powershell
python cli/unity_sdk_agent.py validate mobile-notifications --profile gley-remote-config --no-report --project "<UnityProjectPath>"
```

Do not stop after `install-gley` or `add mobile-notifications`.
