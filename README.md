# Overview

I have developed an Expense Tracker software that allows users to track their expenses. The software is designed to integrate with a cloud database, specifically Firebase, to securely store and manage expense data. This project serves as a practical endeavor to further my learning as a software engineer by gaining hands-on experience with cloud databases and creating a user-friendly expense tracking application.

I have also created a 5 minute demonstration video showcasing the software in action, providing a walkthrough of the code, and demonstrating the integration with the cloud database.

[Software Demo Video](https://www.loom.com/share/cde6d611c8a841a9a146e246757da028?sid=4d1fc355-af6f-4db1-a87d-f42cadc53c02)

# Cloud Database

I have used Firebase as the cloud database solution. Firebase is a cloud-based platform that offers real-time database services, making it an ideal choice for storing and managing expense data securely.

The structure of the Firebase database for this project is organized as follows:

- Users: This collection stores user information, including their email addresses.
  - User_ID: Each user has a unique ID as their key.
    - Expenses: This subcollection contains individual expense records.
      - Expense_ID: Each expense record has a unique ID as its key.
        - Description: Description of the expense.
        - Category: The category to which the expense belongs.
        - Amount: The amount spent on the expense.
        - Date: The date when the expense occurred.

This structure allows each user to have their expenses organized within their own collection, ensuring data privacy and separation.

# Development Environment

- **Programming Language:** Python
- **GUI Toolkit:** Tkinter for creating the graphical user interface.
- **Cloud Database:** Firebase Realtime Database
- **Firebase Libraries:** Pyrebase for Python for interacting with Firebase.
- **Data Visualization:** Matplotlib for creating pie charts to visualize expense categories.
- **Date Picker:** tkcalendar for selecting and displaying dates within the application.

# Useful Websites

During the development of this project, I found the following websites helpful:

- [Firebase Documentation](https://firebase.google.com/docs) - Official documentation for Firebase, which provided guidance on integrating Firebase with Python.
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html) - Official documentation for Tkinter, useful for building the GUI.
- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html) - Official documentation for Matplotlib for data visualization.
- [tkcalendar GitHub](https://github.com/j4321/tkcalendar) - Repository for tkcalendar, which offered information on how to use the date picker widget.
- [Pyrebase GitHub](https://github.com/thisbejim/Pyrebase) - Pyrebase GitHub repository, which provided code examples and usage instructions for Pyrebase.

# Future Work

In the future, I plan to improve and extend this expense tracker software by adding the following features:

1. User Authentication: Enhance user authentication by providing features like password reset and email verification.
2. Data Analytics: Implement more advanced data analysis and visualization features to provide insights into expense patterns.
3. Expense Categories: Allow users to create and manage custom expense categories.
4. Export Reports: Enable users to export expense reports in different formats (e.g., PDF, Excel).
5. Multiple Platforms: Develop versions of the software for mobile and web platforms to provide users with flexibility.

By working on these improvements, I aim to create a more comprehensive and user-friendly expense tracking application that can benefit a wider user base.