import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import Calendar
import pyrebase
import json

# Load Firebase configuration from the JSON file
with open('config.json') as config_file:
    firebase_config = json.load(config_file)

firebase = pyrebase.initialize_app(firebase_config)

# Initialize Firestore
db = firebase.database()

# Get a reference to the authentication service
auth = firebase.auth()

# Create a global variable to store the item ID of the expense to be edited
selected_expense_id = None

# Global variable to store the user's information
user = None

# Function to start the main expense tracking program
def start_expense_program():
    app = tk.Tk()
    app.title('Expense Tracker')

    # Create the notebook for different sections
    notebook = ttk.Notebook(app)    
    notebook.pack(padx=10, pady=10)

    def add_expense():
        description = description_entry.get()
        category = category_entry.get()
        amount = amount_entry.get()
        date = date_calendar.get_date()

        try:
            amount = float(amount)
        except ValueError:
            error_label.config(text="Amount must be a valid number.")
            return

        if description and category:
            data = {
                'description': description,
                'category': category,
                'amount': amount,
                'date': date
            }

            # Store the expense in the user's collection (using their UID as the collection name)
            user_uid = user['localId']
            user_collection = db.child('users').child(user_uid).child('expenses')
            user_collection.push(data)

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

        # Get the existing expense data from the user's collection
        user_uid = user['localId']
        user_collection = db.child('users').child(user_uid).child('expenses')
        expense_ref = user_collection.child(selected_expense_id)
        expense_data = expense_ref.get().val()

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
        description_entry.insert(0, expense_data.get('description', ''))

        category_label = ttk.Label(edit_window, text='Category:')
        category_label.grid(row=1, column=0, padx=5, pady=5)
        category_entry = ttk.Entry(edit_window)
        category_entry.grid(row=1, column=1, padx=5, pady=5)
        category_entry.insert(0, expense_data.get('category', ''))

        amount_label = ttk.Label(edit_window, text='Amount:')
        amount_label.grid(row=2, column=0, padx=5, pady=5)
        amount_entry = ttk.Entry(edit_window)
        amount_entry.grid(row=2, column=1, padx=5, pady=5)
        amount_entry.insert(0, str(expense_data.get('amount', 0.0)))

        # Function to update the expense record in the database
        def save_edited_expense():
            new_description = description_entry.get()
            new_category = category_entry.get()
            new_amount = amount_entry.get()
            new_date = date_calendar.get_date()

            if new_description and new_category and new_amount:
                edited_data = {
                    'description': new_description,
                    'category': new_category,
                    'amount': float(new_amount),
                    'date': new_date
                }
                # Update the expense data in the user's collection with user's idToken
                user_uid = user['localId']
                user_collection = db.child('users').child(user_uid).child('expenses')
                user_collection.child(selected_expense_id).update(edited_data, user['idToken'])

                edit_window.destroy()  # Close the edit window
                update_expense_list()
            else:
                error_label.config(text="Please fill in all the fields.")

        # Create a "Save" button to save the edited expense
        save_button = ttk.Button(edit_window, text='Save', command=save_edited_expense)
        save_button.grid(row=4, columnspan=2, padx=5, pady=10)

    def update_expense_list():
        user_uid = user['localId']
        user_collection = db.child('users').child(user_uid).child('expenses')
        expenses = user_collection.get(user['idToken'])
        
        # Clear existing entries in the Treeview
        expense_list.delete(*expense_list.get_children())
        
        if expenses.each():
            for expense in expenses.each():
                data = expense.val()
                item_id = expense.key()
                description = data.get('description', '')
                category = data.get('category', '')
                amount = data.get('amount', 0.0)
                date = data.get('date', '')
                
                # Insert the updated data into the Treeview
                expense_list.insert('', 'end', values=(description, category, amount, date, item_id))


    def clear_entries():
        description_entry.delete(0, 'end')
        category_entry.delete(0, 'end')
        amount_entry.delete(0, 'end')

    def delete_selected_expense():
        # Get the selected expense from the Treeview
        selected_item = expense_list.selection()
        if selected_item:
            item_id = expense_list.item(selected_item, "values")[4]
            
            # Delete the selected expense from the user's collection
            user_uid = user['localId']
            user_collection = db.child('users').child(user_uid).child('expenses')
            user_collection.child(item_id).remove(user['idToken'])
            
            # Update the expense list to reflect the deletion
            update_expense_list()
            clear_entries()

    def generate_report():
        # Retrieve expenses from the user's collection using the user's idToken
        user_uid = user['localId']
        user_collection = db.child('users').child(user_uid).child('expenses')
        expenses = user_collection.get(user['idToken'])

        categories = {}
        
        if expenses.each():
            for expense in expenses.each():
                data = expense.val()
                category = data.get('category', '')
                amount = data.get('amount', 0.0)

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

# Function to create the authentication window
def create_auth_window():
    auth_window = tk.Tk()
    auth_window.title('Login or Signup')

    # Function to handle user login
    def login():
        email = email_entry.get()
        password = password_entry.get()

        try:
            global user
            user = auth.sign_in_with_email_and_password(email, password)

            # Check if the user's collection exists before creating it
            user_uid = user['localId']
            user_collection = db.child('users').child(user_uid)
            if not user_collection.get(user['idToken']).val():
                user_collection.set({'email': email})

            # If login is successful, close the authentication window and proceed to the main program
            auth_window.destroy()
            start_expense_program()
        except Exception as e:
            error_label.config(text="Login failed. Please check your credentials.")

    # Function to handle user signup
    def signup():
        email = email_entry.get()
        password = password_entry.get()

        try:
            global user
            user = auth.create_user_with_email_and_password(email, password)

            # Check if the user's collection exists before creating it
            user_uid = user['localId']
            user_collection = db.child('users').child(user_uid)
            if not user_collection.get(user['idToken']).val():
                user_collection.set({'email': email})

            # If signup is successful, close the authentication window and proceed to the main program
            auth_window.destroy()
            start_expense_program()
        except Exception as e:
            error_label.config(text="Signup failed. Please check your credentials.")

    email_label = ttk.Label(auth_window, text='Email:')
    email_label.grid(row=0, column=0, padx=5, pady=5)
    email_entry = ttk.Entry(auth_window)
    email_entry.grid(row=0, column=1, padx=5, pady=5)

    password_label = ttk.Label(auth_window, text='Password:')
    password_label.grid(row=1, column=0, padx=5, pady=5)
    password_entry = ttk.Entry(auth_window, show='*')
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    login_button = ttk.Button(auth_window, text='Login', command=login)
    login_button.grid(row=2, column=0, padx=5, pady=10)

    signup_button = ttk.Button(auth_window, text='Signup', command=signup)
    signup_button.grid(row=2, column=1, padx=5, pady=10)

    error_label = ttk.Label(auth_window, text="", foreground="red")
    error_label.grid(row=3, columnspan=2, padx=5, pady=10)

    auth_window.mainloop()

# Call the function to create the authentication window
create_auth_window()