# Unity SDK Agent Plugin

![Unity SDK Agent Plugin banner](docs/assets/banner.svg)

[![Status](https://img.shields.io/badge/status-MVP-1f8a70)](#current-scope)
[![Unity](https://img.shields.io/badge/Unity-mobile%20SDKs-0b5cad)](#first-integration)
[![Agent Ready](https://img.shields.io/badge/agent--ready-Codex%20%7C%20Claude%20%7C%20Antigravity-2f4858)](#use-with-ai-agents)
[![License](https://img.shields.io/badge/license-MIT-3d405b)](LICENSE)

Agent-ready Unity SDK integration packs for Codex, Claude, Antigravity, and other AI coding agents.

This repo gives AI coding agents exact recipes, templates, validators, and CLI tools so SDK integrations are repeatable instead of guessed from scratch every time.

## What It Does

```text
Developer request
  -> AI coding agent reads this plugin
  -> Recipe selects exact SDK steps
  -> CLI/templates apply safe changes
  -> Validator checks the result
  -> Agent summarizes what changed
```

![Architecture diagram](docs/assets/architecture.svg)

## First Integration

`mobile-notifications`

- Installs Unity's official `com.unity.mobile.notifications` package.
- Generates a direct Unity Mobile Notifications wrapper for simple projects.
- Provides a production validation profile for Gley + Firebase Remote Config setups.
- Captures a real working project pattern using splash-scene `NotificationsManager`, Android define symbols, notification icons, and Remote Config activation.

## Quick Use

Add mobile notifications:

```powershell
python cli/unity_sdk_agent.py add mobile-notifications --project "D:\Path\To\UnityProject"
```

Validate only:

```powershell
python cli/unity_sdk_agent.py validate mobile-notifications --project "D:\Path\To\UnityProject"
```

Validate a Gley + Firebase Remote Config production setup:

```powershell
python cli/unity_sdk_agent.py validate mobile-notifications --profile gley-remote-config --project "D:\Path\To\UnityProject"
```

Use `--no-report` when you want validation output without writing `IntegrationAgentReports/` into the Unity project.

## Use With AI Agents

Give Codex, Claude, Antigravity, or another coding agent this prompt:

```text
Use this repo as the Unity SDK Agent Plugin.
Read codex/SKILL.md first.
Add mobile notifications to my Unity project.
Validate after changes and summarize the report.
```

For an existing Gley + Firebase setup:

```text
Use this repo as the Unity SDK Agent Plugin.
Validate mobile notifications with the gley-remote-config profile.
Do not modify the project; use --no-report if running the CLI.
```

## Repo Layout

```text
core/
  integrations/
    mobile-notifications/
      recipe.md
      recipe.yaml
      implementation-profile-gley-remote-config.md
      templates/
codex/
  SKILL.md
claude/
  CLAUDE.md
antigravity/
  instructions.md
cli/
  unity_sdk_agent.py
docs/
  assets/
mcp/
  README.md
```

## Current Scope

This is version `0.1`. It focuses on proving the agent-plugin system with one integration.

Mobile notifications currently includes two profiles:

- `basic`: direct Unity Mobile Notifications wrapper.
- `gley-remote-config`: validates a real production-style setup using Gley Mobile Push Notifications, Firebase Remote Config, Android define symbols, splash-scene manager placement, and notification icon settings.

## Documentation

- [Quickstart](QUICKSTART.md)
- [How It Works](docs/how-it-works.md)
- [Mobile Notifications Integration](core/integrations/mobile-notifications/README.md)
- [Gley + Firebase Remote Config Profile](core/integrations/mobile-notifications/implementation-profile-gley-remote-config.md)
- [Roadmap](docs/roadmap.md)
- [Contributing New SDK Packs](docs/contributing.md)
- [Example Prompts](examples/prompts.md)

## Planned SDK Packs

- Crash reporting
- Analytics foundation
- Remote Config
- Localization
- Haptics
- Debug console
- Build info generator

## Important Notes

- This repo does not bundle paid third-party SDKs such as Gley. It validates and wires projects that already include them.
- Firebase dashboard values still need to be configured in Firebase.
- Mobile notification behavior must be tested on a real Android device.
