import threading
import create_query
from database_connector import DatabaseConnector
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import tkcalendar
import os

# Get the base directory of the current file
basedir = os.path.dirname(__file__)


class Application(tk.Tk, DatabaseConnector):
    """
    A Tkinter-based GUI application for querying statistics from a database.

    Attributes:
        resize (bool): Flag for window resizable property.
        dropdown_box_selection (str): The selected product value from the dropdown.

    Methods:
        create_widgets(): Set up and layout GUI components.
        convertToProgramIdentifier(): Convert selected product name in the dropdown to a program name.
        send_query(): Trigger a separate thread to handle the database query.
        send_query_thread(): Perform the database query in a separate thread to prevent freezing windows.
        on_closing(): Handle the closing event of the main window.
        open_tabs_window(arr): Open a new window to display query results.

    """

    def __init__(self):
        """
        Initialize the Application.

        Sets up the main window with title, size, and initial attributes.

        """
        super().__init__()
        self.title("CTS Statistics Input")
        self.geometry("1000x600")
        self.resize = False
        self.resizable(self.resize, self.resize)
        self.dropdown_box_selection = ''
        self.create_widgets()

    def create_widgets(self):
        """
        Create and layout GUI components.

        Components:
            - Dropdown menu for selecting a product.
            - Calendars for selecting start and end dates.
            - Button to send a query.
            - Progress bar for indicating query processing.

        """
        frame = ttk.Frame(self)
        frame.pack(padx=20, pady=20)

        # Dropdown menu
        label = ttk.Label(frame, text="Select the Product: ")
        label.grid(row=0, column=1, padx=5, pady=50)

        values = ['K5', 'K123s', 'ShotTimer', 'HUD', 'Drop', 'SpeedCoach', 'Coxbox']
        self.dropdown_box_selection = ttk.Combobox(frame, values=values)
        self.dropdown_box_selection.grid(row=0, column=2, padx=5, pady=50)

        # Calendar for start date
        start_label = ttk.Label(frame, text="Start Date:")
        start_label.grid(row=1, column=0, padx=5, pady=5)

        self.start_calendar = tkcalendar.Calendar(frame, selectmode='day')
        self.start_calendar.grid(row=1, column=1, padx=5, pady=5)

        # Calendar for end date
        end_label = ttk.Label(frame, text="End Date:")
        end_label.grid(row=1, column=2, padx=5, pady=5)

        self.end_calendar = tkcalendar.Calendar(frame, selectmode='day')
        self.end_calendar.grid(row=1, column=3, padx=5, pady=5)

        # Button to send query
        send_query_button = ttk.Button(frame, text="Send Query", command=self.send_query)
        send_query_button.grid(row=9, column=2, columnspan=1, padx=50, pady=40)

        # Loading bar
        self.loading_bar = ttk.Progressbar(frame, orient='horizontal', length=200, mode='indeterminate')
        self.loading_bar.grid(row=10, column=2, columnspan=1, padx=50, pady=10)

    def convertToProgramIdentifier(self):
        """
        Convert the selected product name in the dropdown to a program name.

        Uses predefined mappings to convert the selected value.

        """
        i = 0
        dropdown_items = ['K5', 'K123s', 'ShotTimer', 'HUD', 'Drop', 'SpeedCoach', 'Coxbox']
        key = ['k5', ['k123', 'k3550', 'k2700', "#Multiple_Params"], 'kst', 'hud', 'drop', '457042', 'coxbox']
        string = self.dropdown_box_selection.get()
        for row in dropdown_items:
            if string == row:
                self.dropdown_box_selection.set(key[i])
                break
            i += 1
        print(self.dropdown_box_selection.get())

    def send_query(self):
        """
        Trigger a separate thread to handle the database query.

        """
        threading.Thread(target=self.send_query_thread).start()

    def send_query_thread(self):
        """
        Perform the database query in a separate thread.

        - Convert selected product name using convertToProgramIdentifier.
        - Extract start and end dates.
        - Create a query using create_query module.
        - Remove repeated Step_IDs and display in a new window.

        """
        self.loading_bar.start()
        self.convertToProgramIdentifier()
        start_date = datetime.strptime(str(self.start_calendar.get_date()), "%m/%d/%y").strftime("%Y-%m-%d 00:00:00")
        end_date = datetime.strptime(str(self.end_calendar.get_date()), "%m/%d/%y").strftime("%Y-%m-%d 23:59:59")
        data = create_query.createQuery(start_date, end_date, self.dropdown_box_selection.get())

        # Remove repeated step IDs from the queries output
        unique_ids = {}
        query_results = []
        for row in data:
            if row[0] not in unique_ids:
                unique_ids[row[0]] = True
                query_results.append(row)
        self.loading_bar.stop()
        self.open_tabs_window(query_results)

    def on_closing(self):
        """
        Handle the closing event of the main window.

        Closes the main window.

        """
        self.destroy()

    def open_tabs_window(self, query_results):
        """
        Open a new window to display query results.

        Parameters:
            arr (list): List of query results.

        """
        from tabs_window import TabsWindow
        self.withdraw()

        if query_results == []:
            messagebox.showerror("Error", "Error: No product in specified date range or SQL Overload")

        new_window = TabsWindow(self, query_results, self.start_calendar.get_date(), self.end_calendar.get_date())
        new_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.wait_window(new_window)


if __name__ == "__main__":
    # Instantiate the Application object and start the Tkinter main loop.
    try:
        app = Application()
        app.iconbitmap(os.path.join(basedir, 'CTS.ico'))  # Set the application icon
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Error", str(e))  # Show an error message in case of an exception
