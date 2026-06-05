# Unity SDK Agent Plugin

Agent-ready Unity SDK integration packs for Codex, Claude, Antigravity, and other AI coding agents.

This repo is designed to be installed once as a reusable agent plugin/toolkit. The AI agent provides the reasoning layer; this repo provides exact recipes, templates, validators, and CLI tools so integrations are repeatable.

## First Integration

- Mobile Notifications using Unity's official `com.unity.mobile.notifications` package
- Android-first setup
- Generated C# service wrapper
- Generated Unity Editor test menu
- Validation report

## Quick Use

From this repo:

```powershell
python cli/unity_sdk_agent.py add mobile-notifications --project "D:\Path\To\UnityProject"
```

Validate only:

```powershell
python cli/unity_sdk_agent.py validate mobile-notifications --project "D:\Path\To\UnityProject"
```

## Use With Codex Or Other Agents

Give the agent this instruction:

```text
Use the Unity SDK Agent Plugin. Read codex/SKILL.md and core/integrations/mobile-notifications/recipe.md. Add mobile notifications to my Unity project and validate the result.
```

## Repo Layout

```text
core/
  integrations/
    mobile-notifications/
      recipe.md
      recipe.yaml
      templates/
codex/
  SKILL.md
claude/
  CLAUDE.md
antigravity/
  instructions.md
cli/
  unity_sdk_agent.py
mcp/
  README.md
```

## Current Scope

This is version 0.1. It focuses on proving the plugin system with one integration. Future SDK packs can be added under `core/integrations/`.

## Suggested Agent Prompt

```text
Use this repo as the Unity SDK Agent Plugin.
Read codex/SKILL.md first.
Add mobile notifications to my Unity project.
Validate after changes and summarize the report.
```

