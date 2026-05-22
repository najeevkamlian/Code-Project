import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ================= DATABASE =================

conn = sqlite3.connect("attendance_system.db")
cursor = conn.cursor()

# Create Students Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL
)
""")

# Create Attendance Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    name TEXT,
    date TEXT,
    time TEXT,
    status TEXT
)
""")

conn.commit()

# ================= FUNCTIONS =================

def add_student():
    sid = student_id_entry.get()
    name = student_name_entry.get()

    if sid == "" or name == "":
        messagebox.showerror("Error", "Please fill all fields")
        return

    try:
        cursor.execute(
            "INSERT INTO students (student_id, name) VALUES (?, ?)",
            (sid, name)
        )

        conn.commit()

        messagebox.showinfo("Success", "Student Added Successfully")

        clear_student_fields()
        load_students()

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Student ID already exists")


def mark_attendance(status):
    sid = attendance_id_entry.get()

    if sid == "":
        messagebox.showerror("Error", "Enter Student ID")
        return

    cursor.execute(
        "SELECT name FROM students WHERE student_id=?",
        (sid,)
    )

    result = cursor.fetchone()

    if result:
        name = result[0]

        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        cursor.execute("""
        INSERT INTO attendance
        (student_id, name, date, time, status)
        VALUES (?, ?, ?, ?, ?)
        """, (sid, name, date, time, status))

        conn.commit()

        messagebox.showinfo(
            "Attendance Saved",
            f"{name} marked {status}"
        )

        attendance_id_entry.delete(0, tk.END)
        load_attendance()

    else:
        messagebox.showerror("Error", "Student ID not found")


def load_students():
    for row in student_table.get_children():
        student_table.delete(row)

    cursor.execute("SELECT * FROM students")

    for row in cursor.fetchall():
        student_table.insert("", tk.END, values=row)


def load_attendance():
    for row in attendance_table.get_children():
        attendance_table.delete(row)

    cursor.execute("""
    SELECT student_id, name, date, time, status
    FROM attendance
    ORDER BY id DESC
    """)

    for row in cursor.fetchall():
        attendance_table.insert("", tk.END, values=row)


def clear_student_fields():
    student_id_entry.delete(0, tk.END)
    student_name_entry.delete(0, tk.END)


# ================= GUI WINDOW =================

root = tk.Tk()
root.title("Attendance Management System")
root.geometry("980x620")
root.config(bg="white")

# ================= TITLE =================

title = tk.Label(
    root,
    text="Attendance Management System",
    font=("Arial", 22, "bold"),
    bg="navy",
    fg="white",
    pady=10
)

title.pack(fill=tk.X)

# ================= ADD STUDENT FRAME =================

student_frame = tk.LabelFrame(
    root,
    text="Add Student",
    font=("Arial", 12, "bold"),
    padx=10,
    pady=10
)

student_frame.place(x=20, y=80, width=350, height=220)

# Student ID
tk.Label(
    student_frame,
    text="Student ID",
    font=("Arial", 11)
).grid(row=0, column=0, pady=10, sticky="w")

student_id_entry = tk.Entry(student_frame, font=("Arial", 11), width=25)
student_id_entry.grid(row=0, column=1)

# Student Name
tk.Label(
    student_frame,
    text="Student Name",
    font=("Arial", 11)
).grid(row=1, column=0, pady=10, sticky="w")

student_name_entry = tk.Entry(student_frame, font=("Arial", 11), width=25)
student_name_entry.grid(row=1, column=1)

# Add Button
add_btn = tk.Button(
    student_frame,
    text="Add Student",
    font=("Arial", 11, "bold"),
    bg="green",
    fg="white",
    width=20,
    command=add_student
)

add_btn.grid(row=2, column=0, columnspan=2, pady=20)

# ================= ATTENDANCE FRAME =================

attendance_frame = tk.LabelFrame(
    root,
    text="Mark Attendance",
    font=("Arial", 12, "bold"),
    padx=10,
    pady=10
)

attendance_frame.place(x=20, y=330, width=350, height=220)

# Student ID Entry
tk.Label(
    attendance_frame,
    text="Student ID",
    font=("Arial", 11)
).grid(row=0, column=0, pady=15)

attendance_id_entry = tk.Entry(
    attendance_frame,
    font=("Arial", 11),
    width=25
)

attendance_id_entry.grid(row=0, column=1)

# Present Button
present_btn = tk.Button(
    attendance_frame,
    text="Mark Present",
    font=("Arial", 11, "bold"),
    bg="blue",
    fg="white",
    width=15,
    command=lambda: mark_attendance("Present")
)

present_btn.grid(row=1, column=0, pady=20)

# Absent Button
absent_btn = tk.Button(
    attendance_frame,
    text="Mark Absent",
    font=("Arial", 11, "bold"),
    bg="red",
    fg="white",
    width=15,
    command=lambda: mark_attendance("Absent")
)

absent_btn.grid(row=1, column=1, pady=20)

# ================= STUDENT TABLE =================

student_table_frame = tk.LabelFrame(
    root,
    text="Student List",
    font=("Arial", 12, "bold")
)

student_table_frame.place(x=400, y=80, width=550, height=220)

student_table = ttk.Treeview(
    student_table_frame,
    columns=("ID", "Name"),
    show="headings"
)

student_table.heading("ID", text="Student ID")
student_table.heading("Name", text="Student Name")

student_table.column("ID", width=150)
student_table.column("Name", width=350)

student_table.pack(fill=tk.BOTH, expand=True)

# ================= ATTENDANCE TABLE =================

attendance_table_frame = tk.LabelFrame(
    root,
    text="Attendance Records",
    font=("Arial", 12, "bold")
)

attendance_table_frame.place(x=400, y=330, width=550, height=220)

attendance_table = ttk.Treeview(
    attendance_table_frame,
    columns=("ID", "Name", "Date", "Time", "Status"),
    show="headings"
)

attendance_table.heading("ID", text="Student ID")
attendance_table.heading("Name", text="Name")
attendance_table.heading("Date", text="Date")
attendance_table.heading("Time", text="Time")
attendance_table.heading("Status", text="Status")

attendance_table.column("ID", width=90)
attendance_table.column("Name", width=120)
attendance_table.column("Date", width=100)
attendance_table.column("Time", width=100)
attendance_table.column("Status", width=100)

attendance_table.pack(fill=tk.BOTH, expand=True)

# ================= LOAD TABLES =================

load_students()
load_attendance()

# ================= RUN APP =================

root.mainloop()