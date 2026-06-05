// Add these defaults when configuring Firebase Remote Config defaults.
{ "isNotificationActive", true },
{ "notificationHours", 24 },

// Apply these values after FirebaseRemoteConfig.DefaultInstance.ActivateAsync() completes.
NotificationsManager.isNotificationActive =
    FirebaseRemoteConfig.DefaultInstance.GetValue("isNotificationActive").BooleanValue;

NotificationsManager.notificationHours =
    (int)FirebaseRemoteConfig.DefaultInstance.GetValue("notificationHours").LongValue;

if (NotificationsManager.isNotificationActive)
{
    NotificationsManager.Instance.Init();
}

