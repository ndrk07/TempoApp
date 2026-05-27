from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.icon_definitions import md_icons
from kivy.core.text import LabelBase
from kivy.core.text import LabelBase
from kivymd.font_definitions import fonts
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemSupportingText
from kivymd.uix.dialog import (MDDialog, MDDialogHeadlineText, MDDialogButtonContainer, MDDialogContentContainer, MDDialogSupportingText)
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldTrailingIcon
from kivymd.uix.pickers import MDModalDatePicker, MDTimePickerDialVertical
from alarm import schedule_alarm
from kivy.utils import platform
from database import init_db, LoadTasksDB, addTask, deleteTask, getNotifyWithID


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
        self.editDialog = MDDialog(
            MDDialogHeadlineText(text="Edit Deadline"),
            MDDialogContentContainer(
                MDDialogSupportingText(text=f"scheduled for {NotifyTime[0][0]}")
            ),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Cancel"), on_release=lambda x: self.editDialog.dismiss()),
                MDButton(MDButtonText(text="Delete"), style="filled", theme_bg_color="Custom", md_bg_color="#D32F2F", on_release=lambda x: self.finalDelete(task_id))
            ),
            spacing="8dp"
        )
        self.editDialog.open()
    def finalDelete(self, task_id):
        deleteTask(task_id)
        if self.editDialog:
            self.editDialog.dismiss()
        self.load_tasks()

    #dialog add task
    def showDialog(self):
        self.taskTitle = MDTextField(MDTextFieldHintText(text="title"), id="taskInput", mode="outlined")
        self.taskDate = MDTextField(MDTextFieldHintText(text="deadline"), MDTextFieldTrailingIcon(icon="calendar"), mode="outlined", readonly=True)
        self.taskDateNotify = MDTextField(MDTextFieldHintText(text="notification"), MDTextFieldTrailingIcon(icon="bell"), mode="outlined", readonly=True)

        self.taskDate.on_touch_down = lambda touch: self.handleTouch(self.taskDate, touch)
        self.taskDateNotify.on_touch_down = lambda touch: self.handleTouch(self.taskDateNotify, touch)

        self.dialog = MDDialog(
            MDDialogHeadlineText(text="Add Deadline"),
            MDDialogContentContainer(
                self.taskTitle,
                self.taskDate,
                self.taskDateNotify,
                orientation="vertical",
                spacing="12dp"
                ),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Cancel"), on_release=lambda x: self.dialog.dismiss()),
                MDButton(MDButtonText(text="Save"), on_release=self.saveTask)
                ),
            spacing="8dp"
        )
        self.dialog.open()

    #date picker
    def handleTouch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.openDatePicker(instance, True, instance)
            return True
        return False
    def openDatePicker(self, instance, value, target):
        if value:
            dateDialog = MDModalDatePicker()
            dateDialog.bind(on_ok=lambda x: self.onDateSave(x, target), on_cancel=lambda x: dateDialog.dismiss())
            dateDialog.open()
    def onDateSave(self, instance, target):
        dates = instance.get_date()
        if dates:
            tempDate = str(dates[0])
            instance.dismiss()
            timePicker = MDTimePickerDialVertical()
            timePicker.bind(on_ok=lambda x: self.onTimeSave(x, target, tempDate), on_cancel=lambda x: timePicker.dismiss())
            timePicker.open()
    def onTimeSave(self, instance, target, tempDate):
        timeStr = instance.time.strftime("%H:%M")
        target.text = f"{tempDate} {timeStr}"
        instance.dismiss()
        target.focus = False

    def saveTask(self, *args):
        if self.taskDate.text == "" or self.taskDateNotify.text == "" or self.taskTitle.text == "": return
        notify = []
        notify.append(self.taskDateNotify.text)
        task_id = addTask(self.taskTitle.text, self.taskDate.text, notify)
        if platform == "android":
            schedule_alarm(task_id, self.taskTitle.text, self.taskDateNotify.text)

        self.load_tasks()
        self.dialog.dismiss()




if "__main__" == __name__:
    DeadlineApp().run()
