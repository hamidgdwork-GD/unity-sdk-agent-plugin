# Unity SDK Integration

Use this skill when a user asks to add, validate, or explain Unity SDK integrations.

## Rules

- Always inspect the Unity project before modifying files.
- Prefer the CLI tool in `cli/unity_sdk_agent.py` for supported integrations.
- Do not invent SDK steps when a recipe exists.
- Read the selected recipe before running an integration.
- Validate after applying an integration.
- Report changed files, validation status, and manual steps.
- Ask before destructive actions. This plugin does not delete project files.

## Supported Integrations

- `mobile-notifications`: Adds Unity's official Mobile Notifications package, generates a service wrapper, generates an editor test menu, and validates the setup.

## Standard Flow

1. Confirm the target path is a Unity project.
2. Read `core/integrations/<integration-id>/recipe.md`.
3. Run:

```powershell
python cli/unity_sdk_agent.py add <integration-id> --project "<UnityProjectPath>"
```

4. If the add command succeeds, summarize the generated report.
5. If it fails, inspect the report and only fix issues related to the integration.

## Mobile Notifications Example

```powershell
python cli/unity_sdk_agent.py add mobile-notifications --project "D:\Projects\MyUnityGame"
```

Validation only:

```powershell
python cli/unity_sdk_agent.py validate mobile-notifications --project "D:\Projects\MyUnityGame"
```

