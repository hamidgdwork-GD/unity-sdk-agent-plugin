#if UNITY_EDITOR
using System;
using IntegrationAgent.Notifications;
using UnityEditor;
using UnityEngine;

namespace IntegrationAgent.Editor
{
    public static class MobileNotificationTestMenu
    {
        [MenuItem("Tools/Integration Agent/Mobile Notifications/Schedule Test Notification")]
        public static void ScheduleTestNotification()
        {
            MobileNotificationService.ScheduleNotification(
                "Test Notification",
                "Mobile notifications are wired into this project.",
                TimeSpan.FromSeconds(10));

            Debug.Log("Scheduled a test notification for 10 seconds from now. Test on an Android device.");
        }

        [MenuItem("Tools/Integration Agent/Mobile Notifications/Cancel All Notifications")]
        public static void CancelAllNotifications()
        {
            MobileNotificationService.CancelAllNotifications();
            Debug.Log("Cancelled all scheduled and displayed mobile notifications.");
        }
    }
}
#endif

