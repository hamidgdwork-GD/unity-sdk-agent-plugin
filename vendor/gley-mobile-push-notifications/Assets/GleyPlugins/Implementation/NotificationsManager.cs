using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Unity.Collections;
using UnityEngine;
using Random = UnityEngine.Random;

#if UNITY_ANDROID
using Unity.Notifications.Android;
#elif UNITY_IOS
using Unity.Notifications.iOS;
#endif

[Serializable]
public class Notification
{
    [Header("Notification: ID")]
    public int id;
    [Header("Notification: Icons")]
    public string iconLarge = "commonicon";
    public string iconSmall = "smallicon";
    [Header("Notification: TimeSpan")]
    public int hours = 24;
    public int minutes = 0;
    public int seconds = 0;
    [Header("Notification: Titles")]
    [Multiline(3)]
    public List<string> allTitles;
    public string title = "Pilot Simulator";
    [Header("Notification: Desc")]
    public string desc = "Your aircraft is fueled up and the skies are clear!";
    [Header("Notification: IntentDataString")]
    public string intentDataString = "common";
    [Header("Notification: EventString")]
    public string eventString = "OpenFromNotification_NewDay";
}

public class NotificationsManager : MonoBehaviour
{
    public static NotificationsManager Instance;
    public static bool isNotificationActive = true;
    public static int notificationHours  = 24;
    
    [Header("Debug")]
    public bool isDebug = false;
    public bool isDebugTime = false;
    [ReadOnly] public string currentIntentData;
    
    [Header("Analytics")]
    public bool sendAnalytics = false;
    
    [Header("Initialization")]
    public bool initOnStart = true;
    
    [Header("Notification: NewDay : DebugTimeSpan")]
    public int hoursDebug;
    public int minutesDebug;
    public int secondsDebug = 15;
    private TimeSpan debugTimeSpan;

    [Header("Notification: New Day!")]
    public Notification notifyNewDay;
    
    private void Awake()
    {
        if (Instance == null) Instance = this;
        DontDestroyOnLoad(gameObject);
    }

    private void Start()
    {
        if (initOnStart) Init();
    }

    public void Init()
    {
        if (!isNotificationActive) return;
        if (!PlayerPrefs.HasKey("ReqNotifyStatus"))
        {
            ShowNotificationPerReq();
            //ScheduleORShowNotificationPerReq();
        }
        notifyNewDay.hours = notificationHours;
        if (isDebugTime) SetNewDayTimeSpanDebug();
        InitializeNotifications();
    }
    
    // void ScheduleORShowNotificationPerReq()
    // {
    //     if (PlayerPrefs.HasKey(GameConstants.playerCashPref)) // all previous builds & new user 2nd time app opens
    //     {
    //         if (PrefsManager.notifyPerReqNewUser == 0)
    //         {
    //             if(isDebug) Debug.LogError("Pop Notification Request: On Start");
    //         }
    //         else
    //         {
    //             ScheduleNotificationPerReq();
    //             if(isDebug) Debug.LogError("Schedule Notification Request: On Lvl Up");
    //         }
    //     }
    //     else // first app open => new user
    //     {
    //         PrefsManager.notifyPerReqNewUser = 1; // For new user 2nd time app open as he will have playerCashPref set when he opens app 2nd time.
    //         ScheduleNotificationPerReq();
    //         if(isDebug) Debug.LogError("Schedule Notification Request: On Lvl Up");
    //     }
    // }

    public void SetNewDayTimeSpanDebug()
    {
        debugTimeSpan = new TimeSpan(hoursDebug, minutesDebug, secondsDebug);
        SetTimeSpan(notifyNewDay, debugTimeSpan);
        if (isDebug) Debug.LogError("SetNewDayTimeSpanDebug | H:" + hoursDebug + " M:" + minutesDebug + " S:" + secondsDebug + " | TimeSpan: " + debugTimeSpan);
    }

    #region Notification Permission Requests
    
    // public void ScheduleNotificationPerReq()
    // {
    //     if (!PlayerPrefs.HasKey("ReqNotifyStatus"))
    //     {
    //         GameConstants.permissionScheduled = true;
    //     }
    // }
    
    // public void ShowSchNotificationPerReq()
    // {
    //     if (GameConstants.permissionScheduled)
    //     {
    //         if(isDebug) Debug.LogError("Pop Notification Request: On Lvl Up");
    //         ShowNotificationPerReq();
    //         GameConstants.permissionScheduled = false;
    //     }
    // }
    
    public void ShowNotificationPerReq()
    {
        if (!PlayerPrefs.HasKey("ReqNotifyStatus"))
        {
            StartCoroutine(ReqNotificationPer());
        }
    }
    
    public IEnumerator ReqNotificationPer()
    {
        if(isDebug) Debug.LogError("Requesting notification permission...");

        // Check if the user has already been prompted
        if (PlayerPrefs.HasKey("ReqNotifyStatus") && PlayerPrefs.GetInt("ReqNotifyStatus") == 1)
        {
            if(isDebug) Debug.LogError("Notification permission already requested.");
            yield break;
        }

        #if UNITY_ANDROID
            yield return ReqNotificationPerAndroid();
        #elif UNITY_IOS
            yield return ReqNotificationPerIOS();
        #else
            Debug.LogWarning("RequestNotificationPermission: Notifications are not supported on this platform.");
        #endif
    }
    
    #if UNITY_ANDROID
    private IEnumerator ReqNotificationPerAndroid()
    {
        if(isDebug) Debug.LogError("Requesting notification permission on Android...");
        var request = new PermissionRequest();
        while (request.Status == PermissionStatus.RequestPending) yield return null;
        
        PlayerPrefs.SetInt("ReqNotifyStatus", 1); // Mark as requested
        TrackNotificationAnalyticsEvent("Notifications_Permission_Shown");
        if (request.Status == PermissionStatus.Allowed)
        {
            if(isDebug) Debug.LogError("Notification permission granted on Android!");
            TrackNotificationAnalyticsEvent("Notifications_Permission_Allowed");
            InitializeNotifications();
        }
        else
        {
            if(isDebug) Debug.LogError("Notification permission denied on Android.");
            TrackNotificationAnalyticsEvent("Notifications_Permission_Denied");
        }
    }
    #endif

    #if UNITY_IOS
    private IEnumerator ReqNotificationPerIOS()
    {
        if(isDebug) Debug.LogError("Requesting notification permission on iOS...");

        // Request iOS notification permissions
        var authorizationRequest = new AuthorizationRequest(
            AuthorizationOption.Alert | AuthorizationOption.Badge | AuthorizationOption.Sound,
            true);

        while (!authorizationRequest.IsFinished)
        {
            yield return null;
        }

        PlayerPrefs.SetInt("ReqNotifyStatus", 1); // Mark as requested
        //if (sendAnalytics) AnalyticsManager.Instance.Send_DesignEvent_Firebase_GA("Notifications_Permission_Shown");

        if (authorizationRequest.Granted)
        {
            if(isDebug) Debug.LogError("Notification permission granted on iOS!");
            //if (sendAnalytics) AnalyticsManager.Instance.Send_DesignEvent_Firebase_GA("Notifications_Permission_Allowed");
            InitializeNotifications();
        }
        else
        {
            if(isDebug) Debug.LogError("Notification permission denied on iOS.");
            //if (sendAnalytics) AnalyticsManager.Instance.Send_DesignEvent_Firebase_GA("Notifications_Permission_Denied");
        }

        authorizationRequest.Dispose();
    }
    #endif
    
    #endregion
    
    public void InitializeNotifications()
    {
        CancelAllNotifications();
        if(!AreNotificationsAllowed()) return;
        if (sendAnalytics) SendAppOpenFromNotificationEvent();
        GleyNotifications.Initialize();
        CancelAllNotifications();
        if (isDebug) Debug.LogError("Notifications Initialized & Reset");
    }
    
    public void CancelAllNotifications()
    {
        #if UNITY_ANDROID
            AndroidNotificationCenter.CancelNotification(notifyNewDay.id);
            if (isDebug) Debug.LogError("AND: Notification Cancelled At ID : " + notifyNewDay.id);
            AndroidNotificationCenter.CancelAllNotifications();
            AndroidNotificationCenter.CancelAllDisplayedNotifications();
            AndroidNotificationCenter.CancelAllScheduledNotifications();
            if (isDebug) Debug.LogError("AND: All Notifications Cancelled");
        #elif UNITY_IOS
            iOSNotificationCenter.RemoveAllScheduledNotifications();
            iOSNotificationCenter.RemoveAllDeliveredNotifications();
            if (isDebug) Debug.LogError("IOS: All Notifications Cancelled");
        #endif
    }
        
    public static bool AreNotificationsAllowed()
    {
        #if UNITY_ANDROID
            var status = AndroidNotificationCenter.UserPermissionToPost;
            return status == PermissionStatus.Allowed;
        #elif UNITY_IOS
            return iOSNotificationCenter.GetNotificationSettings().AuthorizationStatus == AuthorizationStatus.Authorized;
        #else
            return false;
        #endif
    }

    private void SendAppOpenFromNotificationEvent()
    {
        TrackNotificationAnalyticsEvent("Notifications_Initialized");
        currentIntentData = GleyNotifications.AppWasOpenFromNotification();
        if (currentIntentData == null) return;
        if (isDebug) Debug.LogError(" : Notifications Intend Data : " + currentIntentData);
        if (currentIntentData == notifyNewDay.intentDataString)
        {
            TrackNotificationAnalyticsEvent(notifyNewDay.eventString);
        }
    }

    private void TrackNotificationAnalyticsEvent(string eventName)
    {
        if (!sendAnalytics || string.IsNullOrEmpty(eventName)) return;

        try
        {
            var firebaseType = AppDomain.CurrentDomain
                .GetAssemblies()
                .SelectMany(assembly => assembly.GetTypes())
                .FirstOrDefault(type => type.Name == "firebasecall");
            if (firebaseType == null) return;

            var instance = firebaseType
                .GetProperty("Instance", BindingFlags.Public | BindingFlags.Static)
                ?.GetValue(null);
            if (instance == null) return;

            firebaseType
                .GetMethod("Event", BindingFlags.Public | BindingFlags.Instance, null, new[] { typeof(string) }, null)
                ?.Invoke(instance, new object[] { eventName });
        }
        catch (Exception exception)
        {
            if (isDebug) Debug.LogWarning("Notification analytics event failed: " + exception.Message);
        }
    }

    private string title;
    private string desc;
    private string smallIcon;
    private string largeIcon;
    private string intentData;
    //private TimeSpan timeDelayFromNow;
    public void SendNotification(Notification notification)
    {
        notification.title = notification.allTitles[Random.Range(0, notification.allTitles.Count)];
        title = notification.title;
        desc = notification.desc;
        //timeDelayFromNow = new TimeSpan(notification.hours, notification.minutes, notification.seconds);
        smallIcon = notification.iconSmall;
        largeIcon = notification.iconLarge;
        intentData = notification.intentDataString;
        if (notification.seconds > 0 || notification.minutes > 0 || notification.hours > 0)
        {
            if (isDebug)
            {
                Debug.LogError("SendNotification_" 
                               + notification.intentDataString 
                               + " | Notification ID :" + notification.id + " | "
                               + " : Scheduled After : " 
                               + " | Hours :" + notification.hours + " | "
                               + " | Minutes :" + notification.minutes + " | "
                               + " | Seconds :" + notification.seconds + " | ");
            }
            GleyNotifications.SendNotificationOnId(notification.id, title, desc, notification.hours, notification.minutes, notification.seconds, smallIcon, largeIcon, intentData);
        }
    }
    
    public void SendNotification_NewDay()
    {
        if(!AreNotificationsAllowed()) return;
        SendNotification(notifyNewDay);
    }
    
    public void SetTimeSpan(Notification notification, TimeSpan timeSpan)
    {
        notification.hours = timeSpan.Hours;
        notification.minutes = timeSpan.Minutes;
        notification.seconds = timeSpan.Seconds;
    }
    
    private void OnApplicationFocus(bool focus)
    {
        if (focus == false) //user has left app, schedule notifications
        {
            SendNotification_NewDay();
        }
        else //user returns to app, cancel all pending notifications
        {
            InitializeNotifications();
        }
    }
}
