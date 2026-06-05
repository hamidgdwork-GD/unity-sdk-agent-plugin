# Antigravity Instructions

Read the root `AGENTS.md` first.

For Unity mobile notifications, use the full production workflow:

```powershell
python cli/unity_sdk_agent.py configure-gley-notifications --project "<UnityProjectPath>"
```

Then run the Unity-side configurator if possible:

```text
IntegrationAgent.Editor.GleyNotificationUnityConfigurator.ConfigureForBatchmode
```

Then validate:

```powershell
python cli/unity_sdk_agent.py validate mobile-notifications --profile gley-remote-config --no-report --project "<UnityProjectPath>"
```

Do not stop after `install-gley` or `add mobile-notifications`.
