# How It Works

Unity SDK Agent Plugin is an agent-ready toolkit, not a replacement for Codex, Claude, or Antigravity.

The AI coding agent provides reasoning and project awareness. This repo provides the exact SDK knowledge the agent should follow.

## Flow

1. Developer asks an AI coding agent for an SDK integration.
2. The agent reads `codex/SKILL.md` or the matching app instruction file.
3. The agent reads the selected integration recipe.
4. The agent runs the CLI against the Unity project.
5. The CLI patches safe structured files and copies templates.
6. The validator checks that the expected setup exists.
7. The agent summarizes changed files, validation result, and manual steps.

## Why Recipes Matter

SDK integrations are easy to break when an AI guesses. Recipes make the flow repeatable:

- exact package names and versions
- required Unity settings
- required scripts and prefabs
- validation checks
- known manual steps
- production profiles from real projects

## Current Agent Surfaces

| Surface | File |
| --- | --- |
| Codex | `codex/SKILL.md` |
| Claude | `claude/CLAUDE.md` |
| Antigravity | `antigravity/instructions.md` |
| CLI | `cli/unity_sdk_agent.py` |
| MCP | `mcp/README.md` placeholder |

## Safety Model

- The CLI validates Unity project structure before changes.
- Reports are written to `IntegrationAgentReports/` unless `--no-report` is used.
- Third-party paid SDKs are not bundled.
- Device-level behavior still requires real device testing.

