# Quickstart

## With Codex

Open a Unity project in Codex and provide the plugin path or repo link.

Prompt:

```text
Use this repo as the Unity SDK Agent Plugin.
Read AGENTS.md first.
Add/fix mobile notifications in this Unity project.
```

## With Claude Or Antigravity

Use the same prompt, but point the agent at this repository.

```text
Use this repository as the Unity SDK Agent Plugin.
Read AGENTS.md first.
Add/fix mobile notifications in my Unity project: D:\Path\To\UnityProject
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

Configure the full Gley + Firebase notification profile:

```powershell
python cli/unity_sdk_agent.py configure-gley-notifications --project "D:\Path\To\UnityProject"
```

Use this when the project should match the production profile, including Mobile Notification icon settings and startup scene prefab placement.

The agent instructions require the Unity-side settings step. If the agent cannot run Unity batchmode, open Unity and run:

```text
Tools > Integration Agent > Mobile Notifications > Configure Gley Notification Settings
```
