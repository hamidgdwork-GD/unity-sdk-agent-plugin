# Third-Party Assets

This repo may include first-party or owner-approved Unity assets under `vendor/`.

## Gley Mobile Push Notifications

This repository includes a bundled owner-approved copy of Gley Mobile Push Notifications under:

```text
vendor/gley-mobile-push-notifications/Assets/GleyPlugins
```

The `gley-remote-config` profile expects the target Unity project to contain the Gley files under `Assets/GleyPlugins`. If they are missing, an agent may copy the vendored files into the target Unity project after confirming the user wants to install the bundled Gley plugin.

Expected paths:

```text
Assets/GleyPlugins/Notifications/Scripts/GleyNotifications.cs
Assets/GleyPlugins/Notifications/Scripts/NotificationManager.cs
Assets/GleyPlugins/Implementation/NotificationsManager.cs
Assets/GleyPlugins/Implementation/NotificationsManager.prefab
Assets/GleyPlugins/Notifications/Resources/NotificationSettingsData.asset
```

## Safe Workflow

1. Validate whether the target project already contains Gley.
2. If missing, copy `vendor/gley-mobile-push-notifications/Assets/GleyPlugins` into the target project's `Assets/GleyPlugins`.
3. Run the validation profile:

```powershell
python cli/unity_sdk_agent.py validate mobile-notifications --profile gley-remote-config --no-report --project "D:\Path\To\UnityProject"
```

The CLI can perform the copy:

```powershell
python cli/unity_sdk_agent.py install-gley --project "D:\Path\To\UnityProject"
```

It will not overwrite an existing `Assets/GleyPlugins` folder unless `--force` is used.

3. Fix any missing project-specific setup reported by the validator.

## Ownership Note

The bundled Gley files are included only because the repository owner stated they own or have redistribution rights for this plugin. If this repo is reused by another team, verify asset ownership before publishing or redistributing.
