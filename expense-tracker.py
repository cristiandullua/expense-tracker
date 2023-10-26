import tkinter as tk
from tkinter import ttk
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import Calendar

# Initialize Firebase Admin SDK with your credentials
cred = credentials.Certificate("expense-tracker-7603f-firebase-adminsdk-v7b72-d22e70186a.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Create a global variable to store the item ID of the expense to be edited
selected_expense_id = None

def add_expense():
    description = description_entry.get()
    category = category_entry.get()
    amount = amount_entry.get()
    date = date_calendar.get_date()  # Get the selected date from the Calendar widget

    try:
        amount = float(amount)
    except ValueError:
        error_label.config(text="Amount must be a valid number.")
        return

    if description and category:
        expense_ref = db.collection('expenses').document()
        expense_ref.set({
            'description': description,
            'category': category,
            'amount': amount,
            'date': date
        })
        update_expense_list()
        clear_entries()
        error_label.config(text="Expense added successfully.")
    else:
        error_label.config(text="Please fill in all the fields.")


def edit_expense():
    # Get the selected expense from the Treeview
    selected_item = expense_list.selection()
    if not selected_item:
        return

    global selected_expense_id
    selected_expense_id = expense_list.item(selected_item, "values")[4]

    # Create a pop-up window for editing
    edit_window = tk.Toplevel()
    edit_window.title('Edit Expense')

    # Get the existing expense data from the database
    expense_ref = db.collection('expenses').document(selected_expense_id)
    expense_data = expense_ref.get().to_dict()

    # Create a Calendar widget for date selection
    date_label = ttk.Label(edit_window, text='Date:')
    date_label.grid(row=3, column=0, padx=5, pady=5)
    date_calendar = Calendar(edit_window, date_pattern='yyyy-mm-dd')
    date_calendar.grid(row=3, column=1, padx=5, pady=5)

    # Create entry fields for editing
    description_label = ttk.Label(edit_window, text='Description:')
    description_label.grid(row=0, column=0, padx=5, pady=5)
    description_entry = ttk.Entry(edit_window)
    description_entry.grid(row=0, column=1, padx=5, pady=5)
    description_entry.insert(0, expense_data['description'])

    category_label = ttk.Label(edit_window, text='Category:')
    category_label.grid(row=1, column=0, padx=5, pady=5)
    category_entry = ttk.Entry(edit_window)
    category_entry.grid(row=1, column=1, padx=5, pady=5)
    category_entry.insert(0, expense_data['category'])

    amount_label = ttk.Label(edit_window, text='Amount:')
    amount_label.grid(row=2, column=0, padx=5, pady=5)
    amount_entry = ttk.Entry(edit_window)
    amount_entry.grid(row=2, column=1, padx=5, pady=5)
    amount_entry.insert(0, expense_data['amount'])

    # Function to update the expense record in the database
    def save_edited_expense():
        new_description = description_entry.get()
        new_category = category_entry.get()
        new_amount = amount_entry.get()
        new_date = date_calendar.get_date()  # Get the selected date from the Calendar widget

        if new_description and new_category and new_amount:
            expense_ref.update({    
                'description': new_description,
                'category': new_category,
                'amount': float(new_amount),
                'date': new_date
            })
            edit_window.destroy()  # Close the edit window
            update_expense_list()
        else:
            error_label.config(text="Please fill in all the fields.")

    # Create a "Save" button to save the edited expense
    save_button = ttk.Button(edit_window, text='Save', command=save_edited_expense)
    save_button.grid(row=4, columnspan=2, padx=5, pady=10)

def update_expense_list():
    expense_list.delete(*expense_list.get_children())
    expenses = db.collection('expenses').stream()
    for expense in expenses:
        data = expense.to_dict()
        item_id = expense.id
        description = data['description']
        category = data['category']
        amount = data['amount']
        date = data['date']
        expense_list.insert('', 'end', values=(description, category, amount, date, item_id))

def clear_entries():
    description_entry.delete(0, 'end')
    category_entry.delete(0, 'end')
    amount_entry.delete(0, 'end')

def delete_selected_expense():
    selected_item = expense_list.selection()
    if selected_item:
        item_id = expense_list.item(selected_item, "values")[4]
        db.collection('expenses').document(item_id).delete()
        update_expense_list()
        clear_entries()

def generate_report():
    categories = {}
    
    expenses = db.collection('expenses').stream()
    for expense in expenses:
        data = expense.to_dict()
        category = data['category']
        amount = data['amount']

        if category in categories:
            categories[category] += amount
        else:
            categories[category] = amount

    plt.clf()
    plt.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%')
    plt.title('Expense Categories')
    canvas = FigureCanvasTkAgg(plt.gcf(), master=report_frame)
    canvas.get_tk_widget().pack()
    canvas.draw()

# Create the main application window
app = tk.Tk()
app.title('Expense Tracker')

# Create the notebook for different sections
notebook = ttk.Notebook(app)    
notebook.pack(padx=10, pady=10)

# Expense Entry Section
expense_frame = ttk.Frame(notebook)
notebook.add(expense_frame, text='Add Expense')

# Create a Calendar widget for date selection
date_label = ttk.Label(expense_frame, text='Date:')
date_label.grid(row=3, column=0, padx=5, pady=5)
date_calendar = Calendar(expense_frame, date_pattern='yyyy-mm-dd')
date_calendar.grid(row=3, column=1, padx=5, pady=5)

description_label = ttk.Label(expense_frame, text='Description:')
description_label.grid(row=0, column=0, padx=5, pady=5)
description_entry = ttk.Entry(expense_frame)
description_entry.grid(row=0, column=1, padx=5, pady=5)

category_label = ttk.Label(expense_frame, text='Category:')
category_label.grid(row=1, column=0, padx=5, pady=5)
category_entry = ttk.Entry(expense_frame)
category_entry.grid(row=1, column=1, padx=5, pady=5)

amount_label = ttk.Label(expense_frame, text='Amount:')
amount_label.grid(row=2, column=0, padx=5, pady=5)
amount_entry = ttk.Entry(expense_frame)
amount_entry.grid(row=2, column=1, padx=5, pady=5)

add_button = ttk.Button(expense_frame, text='Add Expense', command=add_expense)
add_button.grid(row=4, columnspan=2, padx=5, pady=10)

# Create an error label to display error messages
error_label = ttk.Label(expense_frame, text="", foreground="red")
error_label.grid(row=5, columnspan=2, padx=5, pady=10)

# Expense List Section
list_frame = ttk.Frame(notebook)
notebook.add(list_frame, text='Expense List')

expense_list = ttk.Treeview(list_frame, column=('Description', 'Category', 'Amount', 'Date', 'Item ID'), show='headings')
expense_list.heading('#1', text='Description')
expense_list.heading('#2', text='Category')
expense_list.heading('#3', text='Amount')
expense_list.heading('#4', text='Date')
expense_list.heading('#5', text='Item ID')
expense_list.pack(padx=5, pady=5)

update_expense_list()

edit_button = ttk.Button(list_frame, text='Edit Expense', command=edit_expense)
edit_button.pack(padx=5, pady=10)
delete_button = ttk.Button(list_frame, text='Delete Expense', command=delete_selected_expense)
delete_button.pack(padx=5, pady=10)

# Expense Report Section
report_frame = ttk.Frame(notebook)
notebook.add(report_frame, text='Expense Report')

generate_report_button = ttk.Button(report_frame, text='Generate Report', command=generate_report)
generate_report_button.pack(padx=5, pady=10)

# Start the main event loop
app.mainloop()