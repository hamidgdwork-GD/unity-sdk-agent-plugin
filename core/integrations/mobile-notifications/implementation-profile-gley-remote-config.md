# Gley + Firebase Remote Config Implementation Profile

This profile captures the notification implementation discovered in:

```text
Angry Crocodile Simulator Stickman V3.7.0
```

It should be used when a Unity mobile project already uses Gley Mobile Push Notifications and Firebase Remote Config.

## Required Packages And Assets

- `Packages/manifest.json`
  - `com.unity.mobile.notifications`: `2.4.3`
- `Assets/GleyPlugins/Notifications/Scripts/GleyNotifications.cs`
- `Assets/GleyPlugins/Notifications/Scripts/NotificationManager.cs`
- `Assets/GleyPlugins/Implementation/NotificationsManager.cs`
- `Assets/GleyPlugins/Implementation/NotificationsManager.prefab`
- `Assets/GleyPlugins/Notifications/Resources/NotificationSettingsData.asset`
- Mobile Notifications Project Settings configured through Unity's editor API
- `Assets/Scripts/firebasecall.cs` or equivalent Firebase Remote Config bootstrap script
- First enabled build scene containing a `NotificationsManager` object or prefab instance

## Required Android Define Symbol

`ProjectSettings/ProjectSettings.asset` should include:

```text
EnableNotificationsAndroid
```

The Gley runtime wraps Android notification code in:

```csharp
#if EnableNotificationsAndroid
```

Without this symbol, the Gley Android notification code will not compile into the Android build.

## Gley Settings

`NotificationSettingsData.asset` should contain:

```yaml
useForAndroid: 1
```

## Mobile Notification Icons

Unity Mobile Notifications Project Settings should define these Android drawable ids:

```text
commonicon
smallicon
```

The game manager uses:

```csharp
public string iconLarge = "commonicon";
public string iconSmall = "smallicon";
```

Do not directly write `ProjectSettings/NotificationsSettings.asset`. Run the generated Unity Editor configurator so the Mobile Notifications package stores settings through its own API.

## Scene Placement Safety

`NotificationsManager` must be placed by Unity through `EditorSceneManager` and `PrefabUtility`. Do not append prefab YAML to `.unity` files; manual scene serialization can corrupt the splash/startup scene.

## Remote Config Keys

Firebase Remote Config should provide:

| Key | Type | Recommended Default | Purpose |
| --- | --- | --- | --- |
| `isNotificationActive` | bool | `true` | Enables/disables notification initialization remotely. |
| `notificationHours` | long/int | `24` | Controls delay for the New Day notification. |

The Firebase bootstrap should apply the values after activation:

```csharp
NotificationsManager.isNotificationActive = FirebaseRemoteConfig.DefaultInstance.GetValue("isNotificationActive").BooleanValue;
NotificationsManager.notificationHours = (int)FirebaseRemoteConfig.DefaultInstance.GetValue("notificationHours").LongValue;

if (NotificationsManager.isNotificationActive)
{
    NotificationsManager.Instance.Init();
}
```

## Manager Lifecycle

The project-level `NotificationsManager` should:

- Use a singleton `Instance`.
- Call `DontDestroyOnLoad(gameObject)` in `Awake`.
- Keep static remote config fields:
  - `isNotificationActive`
  - `notificationHours`
- Request permission once using `PlayerPrefs` key `ReqNotifyStatus`.
- Call `GleyNotifications.Initialize()` only after permission and activation checks.
- Cancel scheduled/displayed notifications when initializing.
- Schedule the New Day notification from `OnApplicationFocus(false)`.
- Re-initialize/cancel notifications from `OnApplicationFocus(true)`.
- Use `GleyNotifications.SendNotificationOnId(...)` for stable notification ids.
- Read opened notification intent data through `GleyNotifications.AppWasOpenFromNotification()`.

## Validation Command

```powershell
python cli/unity_sdk_agent.py validate mobile-notifications --profile gley-remote-config --project "<UnityProjectPath>"
```
