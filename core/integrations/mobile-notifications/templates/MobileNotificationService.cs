using System;
using Unity.Notifications.Android;
using UnityEngine;

namespace IntegrationAgent.Notifications
{
    public static class MobileNotificationService
    {
        private const string DefaultChannelId = "default_notifications";

        public static void Initialize()
        {
            var channel = new AndroidNotificationChannel
            {
                Id = DefaultChannelId,
                Name = "Default Notifications",
                Importance = Importance.Default,
                Description = "General game notifications"
            };

            AndroidNotificationCenter.RegisterNotificationChannel(channel);
        }

        public static int ScheduleNotification(string title, string text, TimeSpan delay)
        {
            Initialize();

            var notification = new AndroidNotification
            {
                Title = title,
                Text = text,
                FireTime = DateTime.Now.Add(delay),
                SmallIcon = "default",
                LargeIcon = "default"
            };

            return AndroidNotificationCenter.SendNotification(notification, DefaultChannelId);
        }

        public static void CancelNotification(int notificationId)
        {
            AndroidNotificationCenter.CancelScheduledNotification(notificationId);
        }

        public static void CancelAllNotifications()
        {
            AndroidNotificationCenter.CancelAllScheduledNotifications();
            AndroidNotificationCenter.CancelAllDisplayedNotifications();
        }
    }
}

