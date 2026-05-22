import tkinter as tk

# Function to update the display
def press(key):
    current = entry.get()
    entry.delete(0, tk.END)
    entry.insert(tk.END, current + str(key))

# Function to clear display
def clear():
    entry.delete(0, tk.END)

# Function to evaluate expression
def equal():
    try:
        result = eval(entry.get())
        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))
    except:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "Error")


# Create main window
root = tk.Tk()
root.title("Najeev Calculator")
root.geometry("300x400")

# Entry field
entry = tk.Entry(root, font=("Arial", 20), bd=10, relief=tk.RIDGE, justify="right")
entry.grid(row=0, column=0, columnspan=4)

# Button layout
buttons = [
    ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
    ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
    ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
    ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3),
]

# Create buttons
for (text, row, col) in buttons:
    if text == "=":
        btn = tk.Button(root, text=text, width=5, height=2,
                        command=equal)
    else:
        btn = tk.Button(root, text=text, width=5, height=2,
                        command=lambda t=text: press(t))

    btn.grid(row=row, column=col, padx=5, pady=5)

# Clear button
clear_btn = tk.Button(root, text="C", width=22, height=2, command=clear)
clear_btn.grid(row=5, column=0, columnspan=4, padx=5, pady=5)

# Run app
root.mainloop()