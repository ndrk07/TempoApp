from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.icon_definitions import md_icons
from kivy.core.text import LabelBase
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.font_definitions import fonts
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemSupportingText
from kivymd.uix.dialog import (MDDialog, MDDialogHeadlineText, MDDialogButtonContainer, MDDialogContentContainer, MDDialogSupportingText)
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton, MDButtonIcon
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldTrailingIcon
from kivymd.uix.pickers import MDModalDatePicker, MDTimePickerDialVertical
from alarm import schedule_alarm, cancel_alarm
from datetime import datetime, timedelta
from kivy.utils import platform
from database import init_db, LoadTasksDB, addTask, deleteTask, getNotifyWithID, deleteReminder


for font_data in fonts:
    LabelBase.register(**font_data)
class DeadlineApp(MDApp):
    def build(self):
        init_db()
        return Builder.load_file("deadline.kv")
    
    def on_start(self):
        self.load_tasks()
        if platform == "android":
            from android.permissions import request_permissions, Permission #type: ignore
            request_permissions([Permission.POST_NOTIFICATIONS])

    #load deadlines
    def load_tasks(self):
        listView = self.root.ids.task_list
        listView.clear_widgets()
        tasks = LoadTasksDB()
        
        for task_id, title, deadline in tasks:
            editButton = MDIconButton(icon="calendar-edit", theme_icon_color="Custom", icon_color="#49454f",pos_hint={"center_y": .5})
            editButton.bind(on_release=lambda x, tid=task_id: self.editDeadline(tid))
            item = MDListItem(MDListItemHeadlineText(text=title), MDListItemSupportingText(text=deadline), editButton)
            listView.add_widget(item)
    
    #dialog edit deadline
    def editDeadline(self, task_id):
        NotifyTime = getNotifyWithID(task_id)
        self.currentTaskID = task_id

        self.editNotifications = NotifyTime
        self.editNotificationList = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing="10dp", padding="6dp")
        self.buildNotificationList(self.editNotificationList, self.editNotifications, True)
        notificationScroll = MDScrollView()
        notificationsWrapper = MDCard(
            size_hint_y=None,
            height="150dp",
            radius=[15, 15, 15, 15],
            style="filled",
            theme_bg_color="Custom",
            md_bg_color=(37/255, 38/255, 52/255, 1),
        )
        
        notificationScroll.add_widget(self.editNotificationList)
        notificationsWrapper.clear_widgets()
        notificationsWrapper.add_widget(notificationScroll)
        
        self.editDialog = MDDialog(
            MDDialogHeadlineText(text="Edit Deadline"),
            MDDialogContentContainer(
                notificationsWrapper
            ),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Cancel"), on_release=lambda x: self.editDialog.dismiss()),
                Widget(),
                MDButton(MDButtonText(text="Delete"), style="filled", theme_bg_color="Custom", md_bg_color="#D32F2F", on_release=lambda x: self.finalDelete(task_id)),
                spacing="8dp"
            ),
        )
        
        self.editDialog.open()
    def finalDelete(self, task_id):
        if platform == "android":
            reminders = getNotifyWithID(task_id)
            for notify_id, notify_time in reminders:
                cancel_alarm(notify_id)
        deleteTask(task_id)
        if self.editDialog:
            self.editDialog.dismiss()
        self.load_tasks()

    #dialog add task
    def showDialog(self):
        self.taskTitle = MDTextField(MDTextFieldHintText(text="title"), id="taskInput", mode="outlined")
        self.taskDate = MDTextField(MDTextFieldHintText(text="deadline"), MDTextFieldTrailingIcon(icon="calendar"), mode="outlined", readonly=True)
        self.taskDate.on_touch_down = lambda touch: self.handleTouch(self.taskDate, touch)

        self.notifications = []
        self.notificationsList = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing="10dp", padding="6dp")
        notificationScroll = MDScrollView()
        notificationsWrapper = MDCard(
            size_hint_y=None,
            height="150dp",
            radius=[15, 15, 15, 15],
            style="filled",
            theme_bg_color="Custom",
            md_bg_color=(37/255, 38/255, 52/255, 1),
            # padding="10dp"
        )
        notificationScroll.add_widget(self.notificationsList)
        notificationsWrapper.clear_widgets()
        notificationsWrapper.add_widget(notificationScroll)

        self.dialog = MDDialog(
            MDDialogHeadlineText(text="New Deadline"),
            MDDialogContentContainer(
                self.taskTitle,
                self.taskDate,
                MDLabel(text="Notifications"),
                notificationsWrapper,
                MDButton(MDButtonText(text="Set Notifications"), MDButtonIcon(icon="bell"), on_release=self.SetNotificationsDialog),
                orientation="vertical",
                spacing="12dp"
                ),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Cancel"), on_release=lambda x: self.dialog.dismiss()),
                Widget(),
                MDButton(MDButtonText(text="Save"), style="filled", on_release=self.saveTask),
                spacing="8dp"
                ),
        )
        self.dialog.open()
    #agree delete reminder
    def deleteReminderDialog(self, notify_id):
        self.DRDialog = MDDialog(
            MDDialogHeadlineText(text="Delete Reminder?"),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Cancel"), on_release=lambda x: self.DRDialog.dismiss()),
                Widget(),
                MDButton(MDButtonText(text="Delete"), style="filled", theme_bg_color="Custom", md_bg_color="#D32F2F", on_release=lambda x: self.removeReminder(notify_id)),
                spacing="8dp"
            )
        )
        self.DRDialog.open()
    #refresh edit notification list
    def refreshEditNotificationUI(self):
        self.editNotifications = getNotifyWithID(self.currentTaskID)
        self.buildNotificationList(self.editNotificationList, self.editNotifications, True)
    #refresh notification list
    def refreshNotificationsUI(self):
        self.buildNotificationList(self.notificationsList, self.notifications)
    #build NotificationList
    def buildNotificationList(self, container, notifications, edit=False):
        container.clear_widgets()
        for notify in notifications:
            if edit:
                notify_id, notify_text = notify
            else:
                notify_text = notify
            item = MDCard(
                orientation="horizontal",
                size_hint_y=None,
                height="50dp",
                radius=[15, 15, 15, 15],
                padding="16dp",
                spacing="12dp",
                style="filled",
                theme_bg_color="Custom",
                md_bg_color=(67/255, 67/255, 88/255, 1)
            )
            label = MDLabel(
                text=notify_text,
                theme_text_color="Custom",
                text_color=(182/255, 158/255, 239/255, 1),
                halign="left"
            )
            if edit:
                deleteBtn = MDIconButton(
                    icon="trash-can-outline",
                    theme_icon_color="Custom",
                    icon_color=(182/255, 158/255, 239/255, 1),
                    pos_hint={"center_y": 0.5},
                    on_release=lambda x, nid=notify_id: self.deleteReminderDialog(nid)
                )
            else:
                deleteBtn = MDIconButton(
                    icon="trash-can-outline",
                    theme_icon_color="Custom",
                    icon_color=(182/255, 158/255, 239/255, 1),
                    pos_hint={"center_y": 0.5},
                    on_release=lambda x, n=notify_text: self.removeNotification(n)
                )
            content = MDBoxLayout(
                orientation="horizontal"
            )
            content.add_widget(label)
            content.add_widget(deleteBtn)
            
            item.add_widget(content)
            container.add_widget(item)

    #remove Notification
    def removeNotification(self, notif):
        if notif in self.notifications:
            self.notifications.remove(notif)
            self.refreshNotificationsUI()
    #remove Reminder
    def removeReminder(self, notify_id):
        if platform == "android":
            cancel_alarm(notify_id)
        deleteReminder(notify_id)
        self.refreshEditNotificationUI()
        self.DRDialog.dismiss()
    #dialog Set Notifications
    def SetNotificationsDialog(self, *args):
        self.SNDialog = MDDialog(
            MDDialogHeadlineText(text="Selet Reminder"),
            MDDialogContentContainer(
                MDButton(MDButtonText(text="5 minutes before"), on_release=lambda x: self.selectReminder(5)),
                MDButton(MDButtonText(text="30 minutes before"), on_release=lambda x: self.selectReminder(30)),
                MDButton(MDButtonText(text="1 hour before"), on_release=lambda x: self.selectReminder(60)),
                MDButton(MDButtonText(text="Custom"), on_release=self.customReminder),
                orientation="vertical",
                spacing="8dp"
            ),
            spacing="8dp"
        )
        self.SNDialog.open()
    #custom Reminder
    def customReminder(self, *args):
        self.SNDialog.dismiss()
        self.openDatePicker(self.addCustomReminder)
    def addCustomReminder(self, value):
        if value not in self.notifications:
            self.notifications.append(value)
        self.refreshNotificationsUI()
    #Select Reminder
    def selectReminder(self, minutesBefore):
        if not self.taskDate.text:
            return
        
        deadline = datetime.strptime(
            self.taskDate.text,
            "%Y-%m-%d %H:%M"
        )
        notifyTime = deadline - timedelta(minutes=minutesBefore)
        formatted = notifyTime.strftime("%Y-%m-%d %H:%M")
        
        if formatted not in self.notifications:
            self.notifications.append(formatted)
        
        self.refreshNotificationsUI()
        self.SNDialog.dismiss()
    #date picker
    def handleTouch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.openDatePicker(lambda value: self.setFieldText(instance, value))
            return True
        return False
    def setFieldText(self, field, value):
        field.text = value
        field.focus = False
    def openDatePicker(self, callback):
        dateDialog = MDModalDatePicker()
        dateDialog.bind(on_ok=lambda x: self.onDateSave(x, callback), on_cancel=lambda x: dateDialog.dismiss())
        dateDialog.open()
    def onDateSave(self, instance, callback):
        dates = instance.get_date()
        if dates:
            tempDate = str(dates[0])
            instance.dismiss()
            timePicker = MDTimePickerDialVertical()
            timePicker.bind(on_ok=lambda x: self.onTimeSave(x, callback, tempDate), on_cancel=lambda x: timePicker.dismiss())
            timePicker.open()
    def onTimeSave(self, instance, callback, tempDate):
        timeStr = instance.time.strftime("%H:%M")
        finalDate = f"{tempDate} {timeStr}"
        callback(finalDate)
        instance.dismiss()
    #final save task
    def saveTask(self, *args):
        if self.taskDate.text == "" or self.notifications == [] or self.taskTitle.text == "": return

        task_id = addTask(self.taskTitle.text, self.taskDate.text, self.notifications)
        if platform == "android":
            reminders = getNotifyWithID(task_id)
            for notify_id, notifyTime in reminders:
                schedule_alarm(notify_id, self.taskTitle.text, notifyTime)

        self.load_tasks()
        self.dialog.dismiss()




if "__main__" == __name__:
    DeadlineApp().run()
