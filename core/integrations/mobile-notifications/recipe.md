# Mobile Notifications Recipe

Adds local mobile notification support to a Unity project using Unity's official Mobile Notifications package.

## Provider

- Unity Mobile Notifications
- Package name: `com.unity.mobile.notifications`
- Default version: `2.3.2`

## Target

- Unity project
- Android-first
- iOS can be supported later with additional validation and platform notes

## Actions

1. Verify the target folder is a Unity project.
2. Update `Packages/manifest.json` with `com.unity.mobile.notifications`.
3. Generate `Assets/Scripts/Notifications/MobileNotificationService.cs`.
4. Generate `Assets/Editor/IntegrationAgent/MobileNotificationTestMenu.cs`.
5. Validate package entry and generated files.
6. Write an integration report under `IntegrationAgentReports/`.

## Manual Notes

- Test notifications on a real Android device.
- Android 13+ may require runtime notification permission behavior depending on Unity package handling and OS version.
- This recipe provides local notifications, not remote push notifications from a server.

## Validation

The integration is valid when:

- `Packages/manifest.json` exists and contains `com.unity.mobile.notifications`.
- `MobileNotificationService.cs` exists.
- `MobileNotificationTestMenu.cs` exists.

