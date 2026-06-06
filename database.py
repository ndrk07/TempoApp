import sqlite3
import os
from kivy.utils import platform
from datetime import datetime

def getConnection():
    if platform == "android":
        from android.storage import app_storage_path #type: ignore
        dbPath = os.path.join(app_storage_path(), "database.db")
    else:
        dbPath = "database.db"
    return sqlite3.connect(dbPath)

def init_db():
    with getConnection() as conn:
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            deadline TEXT NOT NULL)
                       ''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS reminders (
                            notify_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            task_id INTEGER NOT NULL,
                            notify_at TEXT NOT NULL,
                            is_sent INTEGER DEFAULT 0,
                            FOREIGN KEY (task_id) REFERENCES tasks(task_id))
                       ''')
    conn.close()

# add task
def addTask(title, deadline, notificationTimes):
    with getConnection() as conn:
        cursor = conn.cursor()

        cursor.execute("INSERT INTO tasks (title, deadline) VALUES (?, ?)", (title, deadline))

        lastTaskID = cursor.lastrowid
        for notification in notificationTimes:
            cursor.execute("INSERT INTO reminders (task_id, notify_at) VALUES (?, ?)", (lastTaskID, notification, ))
    conn.close()
    return lastTaskID

#get task where notify = 0
def getTaskNotify():
    with getConnection() as conn:
        cursor = conn.cursor()

        tNow = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute('''SELECT reminders.notify_id, reminders.notify_at, reminders.is_sent, reminders.task_id , tasks.task_id, tasks.title FROM reminders
                        INNER JOIN tasks ON reminders.task_id = tasks.task_id
                        WHERE reminders.is_sent = 0 and reminders.notify_at <= (?)''', (tNow, ))
        data = cursor.fetchall()
    conn.close()
    return data

# get notify
def getNotifyWithID(taskID):
    with getConnection() as conn:
        cursor = conn.cursor()

        cursor.execute('''SELECT notify_id, notify_at FROM reminders WHERE task_id = ?''', (taskID, ))
        notifyTime = cursor.fetchall()
    conn.close()
    return notifyTime

def getActiveReminders(taskID):
    with getConnection() as conn:
        cursor = conn.cursor()
        tNow = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute('''SELECT notify_id, notify_at FROM reminders WHERE task_id = ? AND notify_at > ?''', (taskID, tNow))
        notifyTime = cursor.fetchall()
    conn.close()
    return notifyTime

#mark
def markSent(notifyID):
    with getConnection() as conn:
        cursor = conn.cursor()

        cursor.execute('''UPDATE reminders SET is_sent = 1 WHERE notify_id = (?)''', (notifyID, ))
    conn.close()

#load data
def LoadTasksDB():
    with getConnection() as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM tasks''')
        Tasks = cursor.fetchall()
    conn.close()
    return Tasks

#print Data
def PrintAllData():
    with getConnection() as conn:
        cursor = conn.cursor()

        cursor.execute('''SELECT * FROM tasks''')
        print("Tasks: ", *cursor.fetchall(), sep="\n")
        cursor.execute('''SELECT * FROM reminders''')
        print("Reminders: ", *cursor.fetchall(), sep="\n")
    conn.close()

#delete task
def deleteTask(taskID):
    with getConnection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE task_id = (?)", (taskID, ))
        cursor.execute("DELETE FROM reminders WHERE task_id = (?)", (taskID, ))
    conn.close()

#delete Reminder
def deleteReminder(notify_id):
    with getConnection() as conn:
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM reminders WHERE notify_id = ?''', (notify_id, ))
    conn.close()

if "__main__" == __name__:
    # data = getTaskNotify()
    # print(data)

    # #отправил уведомление

    # for notify in data:
    #     markSent(notify[0])
    data = getNotifyWithID(3)
    for i, j in data:
        print(j)

