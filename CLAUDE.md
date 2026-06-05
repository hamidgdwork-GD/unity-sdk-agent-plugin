# Claude Instructions

Read `AGENTS.md` first.

For Unity mobile notifications, always use the production workflow in `AGENTS.md`. Do not stop after package install or Gley copy.

Required command:

```powershell
python cli/unity_sdk_agent.py configure-gley-notifications --project "<UnityProjectPath>"
```

Then run Unity's editor configurator if possible:

```text
IntegrationAgent.Editor.GleyNotificationUnityConfigurator.ConfigureForBatchmode
```

Then validate:

```powershell
python cli/unity_sdk_agent.py validate mobile-notifications --profile gley-remote-config --no-report --project "<UnityProjectPath>"
```

