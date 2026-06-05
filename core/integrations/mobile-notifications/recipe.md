# Mobile Notifications Recipe

Adds local mobile notification support to a Unity project using Unity's official Mobile Notifications package.

## Provider

- Unity Mobile Notifications
- Package name: `com.unity.mobile.notifications`
- Default version: `2.4.3`
- Optional integration facade: Gley Mobile Push Notifications

## Target

- Unity project
- Android-first
- iOS can be supported later with additional validation and platform notes

## Profiles

### `basic`

Uses Unity Mobile Notifications directly and generates a simple wrapper.

### `gley-remote-config`

Matches the proven production pattern from `Angry Crocodile Simulator Stickman V3.7.0`:

- Unity Mobile Notifications package `2.4.3`
- Gley notification facade in `Assets/GleyPlugins/Notifications`
- Android scripting define symbol `EnableNotificationsAndroid`
- `NotificationsManager` object/prefab in the splash scene
- Firebase Remote Config keys:
  - `isNotificationActive` (`bool`)
  - `notificationHours` (`long/int`)
- Notification icons configured in `ProjectSettings/NotificationsSettings.asset`:
  - large icon id: `commonicon`
  - small icon id: `smallicon`
- Scheduling happens when the app loses focus.
- Pending/displayed notifications are cancelled when the app returns to focus.

## Basic Actions

1. Verify the target folder is a Unity project.
2. Update `Packages/manifest.json` with `com.unity.mobile.notifications`.
3. Generate `Assets/Scripts/Notifications/MobileNotificationService.cs`.
4. Generate `Assets/Editor/IntegrationAgent/MobileNotificationTestMenu.cs`.
5. Validate package entry and generated files.
6. Write an integration report under `IntegrationAgentReports/`.

## Gley + Remote Config Actions

When the project uses Gley notifications and Firebase Remote Config, the agent must also verify or apply these steps:

1. Confirm `Assets/GleyPlugins/Notifications/Scripts/GleyNotifications.cs` exists.
2. Confirm `Assets/GleyPlugins/Notifications/Scripts/NotificationManager.cs` uses `EnableNotificationsAndroid`.
3. Add or confirm Android define symbol `EnableNotificationsAndroid`.
4. Confirm Gley settings asset has `useForAndroid: 1`.
5. Create or confirm a `NotificationsManager` prefab/object.
6. Ensure `NotificationsManager` is present in the splash/first boot scene.
7. Ensure Firebase Remote Config applies `isNotificationActive` and `notificationHours`.
8. Ensure Firebase only calls `NotificationsManager.Instance.Init()` when notifications are active.
9. Validate `commonicon` and `smallicon` exist in Mobile Notifications settings.

## Manual Notes

- Test notifications on a real Android device.
- Android 13+ may require runtime notification permission behavior depending on Unity package handling and OS version.
- This recipe provides local notifications, not remote push notifications from a server.
- This repo includes an owner-approved vendored Gley copy under `vendor/gley-mobile-push-notifications/Assets/GleyPlugins`.
- If Gley is missing, copy the vendored `Assets/GleyPlugins` folder into the target project only after confirming the user wants the bundled plugin installed.
- Firebase dashboard values must be configured manually or through a separate Firebase admin workflow.

## Validation

The integration is valid when:

- `Packages/manifest.json` exists and contains `com.unity.mobile.notifications`.
- `MobileNotificationService.cs` exists.
- `MobileNotificationTestMenu.cs` exists.

For `gley-remote-config`, it is also valid when:

- `EnableNotificationsAndroid` is present in Android scripting define symbols.
- `ProjectSettings/NotificationsSettings.asset` includes `commonicon` and `smallicon`.
- Gley notification scripts exist.
- `Assets/GleyPlugins/Implementation/NotificationsManager.cs` contains remote config flags and focus lifecycle.
- `Assets/GleyPlugins/Implementation/NotificationsManager.prefab` contains the serialized New Day notification data.
- `Assets/Scripts/firebasecall.cs` reads `isNotificationActive` and `notificationHours`, then calls `NotificationsManager.Instance.Init()`.
- `Assets/CodeArchitecture/Scenes/SplashScene.unity` contains `NotificationsManager`.

## Commands

Basic:

```powershell
python cli/unity_sdk_agent.py add mobile-notifications --project "<UnityProjectPath>"
```

Validate the Gley + Firebase Remote Config profile:

```powershell
python cli/unity_sdk_agent.py validate mobile-notifications --profile gley-remote-config --project "<UnityProjectPath>"
```

Install bundled Gley:

```powershell
python cli/unity_sdk_agent.py install-gley --project "<UnityProjectPath>"
```

Configure the full Gley notification profile:

```powershell
python cli/unity_sdk_agent.py configure-gley-notifications --project "<UnityProjectPath>"
```

This command must be used when the user expects the full production setup. It configures these pieces in addition to copying/installing packages:

- Android define symbol `EnableNotificationsAndroid`
- `ProjectSettings/NotificationsSettings.asset` with target-project icon GUIDs
- first enabled build scene prefab placement for `NotificationsManager`
- validation report for the `gley-remote-config` profile
