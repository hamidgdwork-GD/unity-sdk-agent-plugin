#if UNITY_EDITOR
using System;
using System.IO;
using System.Linq;
using Unity.Notifications;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace IntegrationAgent.Editor
{
    public static class GleyNotificationUnityConfigurator
    {
        private const string LargeIconPath = "Assets/GleyPlugins/Icons/commonicon.jpg";
        private const string SmallIconPath = "Assets/GleyPlugins/Icons/smallicon.png";
        private const string NotificationsManagerPrefabPath = "Assets/GleyPlugins/Implementation/NotificationsManager.prefab";

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
            AssetDatabase.Refresh();
            ConfigureNotificationSettings();
            var scenePath = PlaceNotificationsManagerInFirstEnabledScene();
            WriteStatusReport(scenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("Integration Agent: configured Mobile Notifications icons and first enabled scene.");
        }

        private static void ConfigureNotificationSettings()
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
        }

        private static string PlaceNotificationsManagerInFirstEnabledScene()
        {
            var scenePath = EditorBuildSettings.scenes
                .FirstOrDefault(scene => scene.enabled && !string.IsNullOrWhiteSpace(scene.path))
                ?.path;

            if (string.IsNullOrWhiteSpace(scenePath))
            {
                throw new InvalidOperationException("No enabled scene found in File > Build Settings. Add the splash/startup scene at index 0 first.");
            }

            if (!Application.isBatchMode && !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
            {
                throw new OperationCanceledException("User cancelled scene save before notification configuration.");
            }

            var scene = EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
            var existingManager = UnityEngine.Object.FindObjectsOfType<NotificationsManager>(true).FirstOrDefault();
            if (existingManager != null)
            {
                ConfigureManager(existingManager);
                EditorSceneManager.MarkSceneDirty(scene);
                EditorSceneManager.SaveScene(scene);
                Debug.Log($"Integration Agent: NotificationsManager already exists in {scenePath}; refreshed serialized values.");
                return scenePath;
            }

            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(NotificationsManagerPrefabPath);
            if (prefab == null)
            {
                throw new System.IO.FileNotFoundException("Missing NotificationsManager prefab", NotificationsManagerPrefabPath);
            }

            var instance = PrefabUtility.InstantiatePrefab(prefab, scene) as GameObject;
            if (instance == null)
            {
                throw new InvalidOperationException($"Could not instantiate {NotificationsManagerPrefabPath} into {scenePath}.");
            }

            instance.name = "NotificationsManager";
            instance.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);

            var manager = instance.GetComponent<NotificationsManager>();
            if (manager == null)
            {
                throw new MissingComponentException("Instantiated NotificationsManager prefab does not contain a NotificationsManager component.");
            }

            ConfigureManager(manager);
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene);
            Debug.Log($"Integration Agent: placed NotificationsManager in first enabled build scene: {scenePath}");
            return scenePath;
        }

        private static void ConfigureManager(NotificationsManager manager)
        {
            manager.initOnStart = false;
            manager.sendAnalytics = true;
            EditorUtility.SetDirty(manager);
            PrefabUtility.RecordPrefabInstancePropertyModifications(manager);
        }

        private static void WriteStatusReport(string scenePath)
        {
            var projectRoot = Directory.GetParent(Application.dataPath)?.FullName;
            if (string.IsNullOrWhiteSpace(projectRoot))
            {
                throw new InvalidOperationException("Could not resolve Unity project root from Application.dataPath.");
            }

            var reportsDir = Path.Combine(projectRoot, "IntegrationAgentReports");
            Directory.CreateDirectory(reportsDir);
            var reportPath = Path.Combine(reportsDir, "gley-notifications-unity-configurator-status.json");
            var timestamp = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ");
            var json =
                "{\n" +
                "  \"configured_by\": \"IntegrationAgent.Editor.GleyNotificationUnityConfigurator\",\n" +
                "  \"configured_at_utc\": \"" + timestamp + "\",\n" +
                "  \"large_icon_id\": \"commonicon\",\n" +
                "  \"small_icon_id\": \"smallicon\",\n" +
                "  \"notifications_manager_scene\": \"" + scenePath.Replace("\\", "\\\\") + "\",\n" +
                "  \"notifications_manager_prefab\": \"" + NotificationsManagerPrefabPath + "\"\n" +
                "}\n";
            File.WriteAllText(reportPath, json);
            Debug.Log($"Integration Agent: wrote Unity configurator status report: {reportPath}");
        }
    }
}
#endif
