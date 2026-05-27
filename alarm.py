from datetime import datetime
import time
from kivy.utils import platform

if platform == "android":
    from jnius import autoclass

def schedule_alarm(notify_id, title, notifyTime):
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    context = PythonActivity.mActivity

    AlarmManager = autoclass("android.app.AlarmManager")
    Intent = autoclass("android.content.Intent")
    PendingIntent = autoclass("android.app.PendingIntent")
    Context = autoclass("android.content.Context")

    notifyTime = datetime.strptime(notifyTime, "%Y-%m-%d %H:%M")

    triggerTime = int(time.mktime(notifyTime.timetuple()) * 1000)
    
    intent = Intent(context, autoclass("org.test.deadlinesapp.AlarmReceiver"))
    intent.setAction(str(notify_id))
    String = autoclass("java.lang.String")
    intent.putExtra("title", String(title))
    intent.putExtra("message", "Deadline is coming")
    intent.putExtra("notify_id", notify_id)

    pending = PendingIntent.getBroadcast(context, notify_id, intent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE)

    alarm = context.getSystemService(Context.ALARM_SERVICE)
    alarm.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, triggerTime, pending)


def cancel_alarm(notify_id):
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    context = PythonActivity.mActivity

    AlarmManager = autoclass("android.app.AlarmManager")
    Intent = autoclass("android.content.Intent")
    PendingIntent = autoclass("android.app.PendingIntent")
    Context = autoclass("android.content.Context")

    intent = Intent(context, autoclass("org.test.deadlinesapp.AlarmReceiver"))
    intent.setAction(str(notify_id))

    pending = PendingIntent.getBroadcast(context, notify_id, intent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE)

    alarm = context.getSystemService(Context.ALARM_SERVICE)
    alarm.cancel(pending)
    pending.cancel()