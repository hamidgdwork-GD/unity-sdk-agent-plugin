#if UNITY_EDITOR
using Unity.Notifications;
using UnityEditor;
using UnityEngine;

namespace IntegrationAgent.Editor
{
    public static class GleyNotificationUnityConfigurator
    {
        private const string LargeIconPath = "Assets/GleyPlugins/Icons/commonicon.jpg";
        private const string SmallIconPath = "Assets/GleyPlugins/Icons/smallicon.png";

        [MenuItem("Tools/Integration Agent/Mobile Notifications/Configure Gley Notification Settings")]
        public static void ConfigureFromMenu()
        {
            Configure();
        }

        public static void ConfigureForBatchmode()
        {
            Configure();
            EditorApplication.Exit(0);
        }

        public static void Configure()
        {
            var largeIcon = AssetDatabase.LoadAssetAtPath<Texture2D>(LargeIconPath);
            var smallIcon = AssetDatabase.LoadAssetAtPath<Texture2D>(SmallIconPath);

            if (largeIcon == null)
            {
                throw new System.IO.FileNotFoundException("Missing large notification icon", LargeIconPath);
            }

            if (smallIcon == null)
            {
                throw new System.IO.FileNotFoundException("Missing small notification icon", SmallIconPath);
            }

            NotificationSettings.AndroidSettings.RescheduleOnDeviceRestart = true;
            NotificationSettings.AndroidSettings.ExactSchedulingOption = 0;
            NotificationSettings.AndroidSettings.UseCustomActivity = false;
            NotificationSettings.AndroidSettings.CustomActivityString = "com.unity3d.player.UnityPlayerActivity";

            NotificationSettings.AndroidSettings.RemoveDrawableResource("commonicon");
            NotificationSettings.AndroidSettings.RemoveDrawableResource("smallicon");
            NotificationSettings.AndroidSettings.AddDrawableResource("commonicon", largeIcon, NotificationIconType.Large);
            NotificationSettings.AndroidSettings.AddDrawableResource("smallicon", smallIcon, NotificationIconType.Small);

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("Integration Agent: configured Mobile Notifications icons commonicon and smallicon.");
        }
    }
}
#endif

