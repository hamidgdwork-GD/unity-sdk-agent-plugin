using System;
using System.Collections;
using System.Collections.Generic;
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
    public List<string> allTitles = new List<string>
    {
        "Come back for a new mission!",
        "Your next reward is waiting!",
        "A new challenge is ready!"
    };

    public string title = "Game Notification";

    [Header("Notification: Desc")]
    public string desc = "Your next session is ready.";

    [Header("Notification: IntentDataString")]
    public string intentDataString = "common";

    [Header("Notification: EventString")]
    public string eventString = "OpenFromNotification_NewDay";
}

public class NotificationsManager : MonoBehaviour
{
    public static NotificationsManager Instance;
    public static bool isNotificationActive = true;
    public static int notificationHours = 24;

    [Header("Debug")]
    public bool isDebug;
    public bool isDebugTime;
    public string currentIntentData;

    [Header("Analytics")]
    public bool sendAnalytics;

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
        }

        notifyNewDay.hours = notificationHours;
        if (isDebugTime) SetNewDayTimeSpanDebug();
        InitializeNotifications();
    }

    public void SetNewDayTimeSpanDebug()
    {
        debugTimeSpan = new TimeSpan(hoursDebug, minutesDebug, secondsDebug);
        SetTimeSpan(notifyNewDay, debugTimeSpan);
        if (isDebug) Debug.LogError("SetNewDayTimeSpanDebug | H:" + hoursDebug + " M:" + minutesDebug + " S:" + secondsDebug);
    }

    public void ShowNotificationPerReq()
    {
        if (!PlayerPrefs.HasKey("ReqNotifyStatus"))
        {
            StartCoroutine(ReqNotificationPer());
        }
    }

    public IEnumerator ReqNotificationPer()
    {
        if (PlayerPrefs.HasKey("ReqNotifyStatus") && PlayerPrefs.GetInt("ReqNotifyStatus") == 1)
        {
            yield break;
        }

        #if UNITY_ANDROID
        yield return ReqNotificationPerAndroid();
        #elif UNITY_IOS
        yield return ReqNotificationPerIOS();
        #else
        Debug.LogWarning("Notifications are not supported on this platform.");
        #endif
    }

    #if UNITY_ANDROID
    private IEnumerator ReqNotificationPerAndroid()
    {
        var request = new PermissionRequest();
        while (request.Status == PermissionStatus.RequestPending) yield return null;

        PlayerPrefs.SetInt("ReqNotifyStatus", 1);

        if (request.Status == PermissionStatus.Allowed)
        {
            InitializeNotifications();
        }
    }
    #endif

    #if UNITY_IOS
    private IEnumerator ReqNotificationPerIOS()
    {
        var authorizationRequest = new AuthorizationRequest(
            AuthorizationOption.Alert | AuthorizationOption.Badge | AuthorizationOption.Sound,
            true);

        while (!authorizationRequest.IsFinished)
        {
            yield return null;
        }

        PlayerPrefs.SetInt("ReqNotifyStatus", 1);

        if (authorizationRequest.Granted)
        {
            InitializeNotifications();
        }

        authorizationRequest.Dispose();
    }
    #endif

    public void InitializeNotifications()
    {
        CancelAllNotifications();
        if (!AreNotificationsAllowed()) return;
        GleyNotifications.Initialize();
        CancelAllNotifications();
    }

    public void CancelAllNotifications()
    {
        #if UNITY_ANDROID
        AndroidNotificationCenter.CancelNotification(notifyNewDay.id);
        AndroidNotificationCenter.CancelAllNotifications();
        AndroidNotificationCenter.CancelAllDisplayedNotifications();
        AndroidNotificationCenter.CancelAllScheduledNotifications();
        #elif UNITY_IOS
        iOSNotificationCenter.RemoveAllScheduledNotifications();
        iOSNotificationCenter.RemoveAllDeliveredNotifications();
        #endif
    }

    public static bool AreNotificationsAllowed()
    {
        #if UNITY_ANDROID
        return AndroidNotificationCenter.UserPermissionToPost == PermissionStatus.Allowed;
        #elif UNITY_IOS
        return iOSNotificationCenter.GetNotificationSettings().AuthorizationStatus == AuthorizationStatus.Authorized;
        #else
        return false;
        #endif
    }

    public void SendNotification(Notification notification)
    {
        notification.title = notification.allTitles[Random.Range(0, notification.allTitles.Count)];

        if (notification.seconds > 0 || notification.minutes > 0 || notification.hours > 0)
        {
            GleyNotifications.SendNotificationOnId(
                notification.id,
                notification.title,
                notification.desc,
                notification.hours,
                notification.minutes,
                notification.seconds,
                notification.iconSmall,
                notification.iconLarge,
                notification.intentDataString);
        }
    }

    public void SendNotification_NewDay()
    {
        if (!AreNotificationsAllowed()) return;
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
        if (focus == false)
        {
            SendNotification_NewDay();
        }
        else
        {
            InitializeNotifications();
        }
    }
}

