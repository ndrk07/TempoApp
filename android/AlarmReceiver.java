package org.test.deadlinesapp;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.util.Log;

public class AlarmReceiver extends BroadcastReceiver {
    private static final String TAG = "AlarmReceiver";
    private static final String CHANNEL_ID = "deadline_channel";
    private static final String CHANNEL_NAME = "Deadlines";
    private static final String CHANNEL_DESC = "Deadline reminders";

    @Override
    public void onReceive(Context context, Intent intent) {
        try {
            Log.d(TAG, "onReceive extras=" + intent.getExtras());
            String title = intent.getStringExtra("title");
            if (title == null) title = "No title";
            String message = intent.getStringExtra("message");
            if (message == null) message = "Deadline reminder";

            int notifyId = intent.getIntExtra("notify_id", 0);

            NotificationManager manager = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
            if (manager == null) {
                Log.e(TAG, "NotificationManager is null");
                return;
            }
            // Create notification channel for Android O+
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                NotificationChannel channel = new NotificationChannel(
                        CHANNEL_ID,
                        CHANNEL_NAME,
                        NotificationManager.IMPORTANCE_HIGH
                );
                channel.setDescription(CHANNEL_DESC);
                manager.createNotificationChannel(channel);
            }
            // Build PendingIntent to open the app when notification is tapped
            Intent openIntent = context.getPackageManager().getLaunchIntentForPackage(context.getPackageName());
            PendingIntent pendingIntent = null;
            if (openIntent != null) {
                openIntent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
                int flags = PendingIntent.FLAG_UPDATE_CURRENT;
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                    flags |= PendingIntent.FLAG_IMMUTABLE;
                }
                pendingIntent = PendingIntent.getActivity(context, notifyId, openIntent, flags);
            } else {
                Log.w(TAG, "openIntent is null");
            }
            // Check POST_NOTIFICATIONS permission on Android 13+ (API 33)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                if (context.checkSelfPermission("android.permission.POST_NOTIFICATIONS") != PackageManager.PERMISSION_GRANTED) {
                    Log.w(TAG, "POST_NOTIFICATIONS permission not granted; notification may not be shown");
                    // Still attempt to build and notify; system will drop it if permission is missing.
                }
            }
            // Build notification with API-aware constructor
            Notification.Builder builder;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                builder = new Notification.Builder(context, CHANNEL_ID);
            } else {
                builder = new Notification.Builder(context);
            }

            builder.setContentTitle(title)
                   .setContentText(message)
                   .setSmallIcon(android.R.drawable.ic_dialog_info)
                   .setAutoCancel(true);

            if (pendingIntent != null) {
                builder.setContentIntent(pendingIntent);
            }
            // For older APIs, set priority via extras if available
            if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
                builder.setPriority(Notification.PRIORITY_HIGH);
            }

            Log.d(TAG, "about to notify id=" + notifyId + " title=" + title);
            manager.notify(notifyId, builder.build());
        } catch (Exception e) {
            Log.e(TAG, "Exception in onReceive", e);
        }
    }
}