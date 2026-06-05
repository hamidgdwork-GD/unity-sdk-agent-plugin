# Mobile Notifications

Adds Unity local mobile notifications using Unity's official package.

## Command

```powershell
python cli/unity_sdk_agent.py add mobile-notifications --project "D:\Path\To\UnityProject"
```

## Generated Files

- `Assets/Scripts/Notifications/MobileNotificationService.cs`
- `Assets/Editor/IntegrationAgent/MobileNotificationTestMenu.cs`

## Unity Menu

After opening the project in Unity:

```text
Tools > Integration Agent > Mobile Notifications > Schedule Test Notification
Tools > Integration Agent > Mobile Notifications > Cancel All Notifications
```

## Limitations

- This is local notification support, not remote server push.
- Android device testing is required.

