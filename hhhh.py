from tkinter import *
import tkinter.messagebox
from datetime import datetime, timedelta
from plyer import notification  # Make sure to install plyer: pip install plyer
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('todo_list.db')
c = conn.cursor()

# Create a table to store tasks if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS tasks (
             task_name TEXT PRIMARY KEY,
             creation_time TIMESTAMP,
             completion_status INTEGER,
             priority TEXT
             )''')
conn.commit()

# Create the main window
window = Tk()
window.title("To-Do List")

# Function to add a task and check for overdue tasks
def add_task():
    task_text = entry_task.get()
    if task_text:
        current_time = datetime.now()
        priority = priority_var.get()
        c.execute('''INSERT INTO tasks (task_name, creation_time, completion_status, priority)
                     VALUES (?, ?, ?, ?)''', (task_text, current_time, 0, priority))  # 0 for incomplete status
        conn.commit()
        listbox_tasks.delete(0, END)  # Clear the listbox
        display_tasks_from_db()
        entry_task.delete(0, "end")
        check_overdue_tasks()

# Function to delete a task
def delete_task():
    selected_task = listbox_tasks.get(ANCHOR).split(" - ")[0]
    c.execute('''DELETE FROM tasks WHERE task_name = ?''', (selected_task,))
    conn.commit()
    listbox_tasks.delete(ANCHOR)

# Function to mark a task as read
def mark_as_read():
    selected_task = listbox_tasks.get(ANCHOR).split(" - ")[0]
    c.execute('''UPDATE tasks SET completion_status = 1 WHERE task_name = ?''', (selected_task,))
    conn.commit()
    listbox_tasks.delete(ANCHOR)
    listbox_tasks.insert(END, f"{selected_task} - Priority: {task_priority[selected_task]} - {task_creation_times[selected_task]} (Completed)")

# Function to view task details
def view_task():
    selected_task = listbox_tasks.get(ANCHOR).split(" - ")[0]
    task_details = f"Task: {selected_task}\nPriority: {task_priority[selected_task]}\nCreated: {task_creation_times[selected_task]}\nStatus: {'Completed' if task_completion_status[selected_task] else 'Not Completed'}"
    tkinter.messagebox.showinfo("Task Details", task_details)

# Function to check overdue tasks and show notifications
def check_overdue_tasks():
    current_time = datetime.now()
    for task, creation_time in task_creation_times.items():
        if (current_time - creation_time) > timedelta(hours=24):
            tkinter.messagebox.showwarning("Task Overdue", f"The task '{task}' is overdue!")

# Function to search for a task
def search_task():
    search_text = entry_search.get().lower()
    listbox_tasks.delete(0, END)
    c.execute('''SELECT task_name, priority, creation_time FROM tasks''')
    tasks = c.fetchall()
    for task in tasks:
        if search_text in task[0].lower():
            listbox_tasks.insert(END, f"{task[0]} - Priority: {task[1]} - {task[2]}")

# Entry and buttons for adding tasks
entry_task = Entry(window, width=40)
entry_task.pack(pady=10)

priority_var = StringVar(window)
priority_var.set("Low")  # Default priority
priority_label = Label(window, text="Priority:")
priority_label.pack()
priority_dropdown = OptionMenu(window, priority_var, "Low", "Medium", "High")
priority_dropdown.pack()

add_button = Button(window, text="Add Task", width=40, command=add_task)
add_button.pack()

# Buttons for managing tasks
delete_button = Button(window, text="Delete Task", width=40, command=delete_task)
delete_button.pack()

mark_as_read_button = Button(window, text="Mark as Read", width=40, command=mark_as_read)
mark_as_read_button.pack()

view_task_button = Button(window, text="View Task", width=40, command=view_task)
view_task_button.pack()

# Search functionality
entry_search = Entry(window, width=40)
entry_search.pack(pady=10)
search_button = Button(window, text="Search Task", width=40, command=search_task)
search_button.pack()

# Listbox for tasks
listbox_tasks = Listbox(window, bg="lavender", fg="black", height=15, width=50, font="Helvetica")
listbox_tasks.pack()

# Function to display tasks from the database
def display_tasks_from_db():
    listbox_tasks.delete(0, END)  # Clear the listbox
    c.execute('''SELECT task_name, priority, creation_time, completion_status FROM tasks ORDER BY
              CASE
                WHEN priority = 'High' THEN 1
                WHEN priority = 'Medium' THEN 2
                WHEN priority = 'Low' THEN 3
              END''')
    tasks = c.fetchall()
    for task in tasks:
        task_name = task[0]
        priority = task[1]
        creation_time = task[2]
        completion_status = task[3]
        listbox_tasks.insert(END, f"{task_name} - Priority: {priority} - {creation_time}{' (Completed)' if completion_status else ''}")

# Display tasks from the database when the application starts
display_tasks_from_db()

# Start the Tkinter main loop
window.mainloop()