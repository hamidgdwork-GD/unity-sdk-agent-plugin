# Third-Party Assets

This repo does not bundle paid or licensed third-party Unity Asset Store packages.

## Gley Mobile Push Notifications

The `gley-remote-config` profile expects the target Unity project to already contain a licensed copy of Gley Mobile Push Notifications.

Expected paths:

```text
Assets/GleyPlugins/Notifications/Scripts/GleyNotifications.cs
Assets/GleyPlugins/Notifications/Scripts/NotificationManager.cs
Assets/GleyPlugins/Implementation/NotificationsManager.cs
Assets/GleyPlugins/Implementation/NotificationsManager.prefab
Assets/GleyPlugins/Notifications/Resources/NotificationSettingsData.asset
```

## Safe Workflow

1. Import Gley Mobile Push Notifications into the Unity project from the Unity Asset Store or Package Manager using a licensed account.
2. Run the validation profile:

```powershell
python cli/unity_sdk_agent.py validate mobile-notifications --profile gley-remote-config --no-report --project "D:\Path\To\UnityProject"
```

3. Fix any missing project-specific setup reported by the validator.

## Why It Is Not Bundled

Bundling paid third-party SDK code in this repo could violate the package license, even if the repository is private. The plugin stores integration knowledge, validation rules, and safe templates instead.

