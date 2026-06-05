# Quickstart

## With Codex

Open a Unity project in Codex and provide the plugin path or repo link.

Prompt:

```text
Use the Unity SDK Agent Plugin. Read codex/SKILL.md and add mobile notifications to this Unity project. Validate after changes and summarize the report.
```

## With Claude Or Antigravity

Use the same prompt, but point the agent at this repository.

```text
Use this repository as the Unity SDK Agent Plugin. Add mobile notifications to my Unity project using the mobile-notifications recipe.
```

## Direct CLI

```powershell
python cli/unity_sdk_agent.py add mobile-notifications --project "D:\Path\To\UnityProject"
```

For projects that already use Gley Mobile Push Notifications plus Firebase Remote Config:

```powershell
python cli/unity_sdk_agent.py validate mobile-notifications --profile gley-remote-config --project "D:\Path\To\UnityProject"
```

Use `--no-report` when you want validation output without writing `IntegrationAgentReports/` into the Unity project.

Install the bundled Gley plugin into a Unity project:

```powershell
python cli/unity_sdk_agent.py install-gley --project "D:\Path\To\UnityProject"
```

By default, this will not overwrite an existing `Assets/GleyPlugins` folder.
