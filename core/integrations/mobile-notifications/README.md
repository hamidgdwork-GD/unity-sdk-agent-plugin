# Mobile Notifications

Adds Unity local mobile notifications using Unity's official package.

## Command

```powershell
python cli/unity_sdk_agent.py add mobile-notifications --project "D:\Path\To\UnityProject"
```

Validate a project that uses the Gley + Firebase Remote Config pattern:

```powershell
python cli/unity_sdk_agent.py validate mobile-notifications --profile gley-remote-config --project "D:\Path\To\UnityProject"
```

## Generated Files

- `Assets/Scripts/Notifications/MobileNotificationService.cs`
- `Assets/Editor/IntegrationAgent/MobileNotificationTestMenu.cs`

## Production Pattern Captured

This integration also documents the working setup from `Angry Crocodile Simulator Stickman V3.7.0`:

- Gley `NotificationsManager` lives in the splash scene and persists with `DontDestroyOnLoad`.
- Firebase Remote Config controls `NotificationsManager.isNotificationActive` and `NotificationsManager.notificationHours`.
- `NotificationsManager.Instance.Init()` is called only when `isNotificationActive` is true.
- Android code is enabled by `EnableNotificationsAndroid`.
- Notification icons are named `commonicon` and `smallicon`.
- Notifications are scheduled in `OnApplicationFocus(false)` and cancelled/re-initialized in `OnApplicationFocus(true)`.

## Unity Menu

After opening the project in Unity:

```text
Tools > Integration Agent > Mobile Notifications > Schedule Test Notification
Tools > Integration Agent > Mobile Notifications > Cancel All Notifications
```

## Limitations

- This is local notification support, not remote server push.
- Android device testing is required.
- The Gley plugin is bundled under `vendor/gley-mobile-push-notifications/Assets/GleyPlugins` with owner approval.
