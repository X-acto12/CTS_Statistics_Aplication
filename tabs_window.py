import csv
import glob
import os
import subprocess
import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import ttk, filedialog
from DataAnalysis import DataAnalysis
from tkinter import messagebox

"""
    TabsWindow Class

    A Tkinter-based window for displaying detailed query results with multiple tabs.

    Attributes:
        - input_arr (list): The original data obtained from the database query.
        - data_arr (list): Cleaned and filtered data without repeated IDs.
        - dict_data (dict): Cleaned data represented as a dictionary.
        - ids_data (list): Cleaned data specifically for expansion with individual IDs but repeated Serial Numbers.
        - start (str): Start date of the query.
        - end (str): End date of the query.
        - dAsys (DataAnalysis): An instance of the DataAnalysis class for statistical analysis.
        - error_count (list): List of error counts for different error types.
        - expanded (set): Set to keep track of expanded serial numbers.
        - current_sort_order (dict): Dictionary to keep track of the current sort order for each column.

    Methods:
        - create_widgets(): Set up and layout GUI components for different tabs.
        - remove_repeated_ids(): Remove repeated IDs from the original data.
        - createMostRecentSN(): Clean and filter data to keep only the most recent entry for each serial number.
        - repeatedSNForExpansion(): Clean data specifically for expansion with additional details.
        - get_serial_info(): Get information for a specific serial number.
        - open_html_file(): Open the associated HTML file for a clicked ID.
        - show_instances(): Show instances of the selected serial number.
        - download_csv(): Download the unexpanded rows to a .csv file.
        - getFilePath(): Get the file path for the HTML file associated with a serial number.
        - sort_treeview(): Sort the treeview based on the selected column.

    """




class TabsWindow(tk.Toplevel):
    def __init__(self, parent, data, start, end):
        super().__init__(parent)
        # These are all documented in the header
        self.title("CTS Statistics Analyzer")
        self.geometry("1000x600")
        self.input_arr = data
        self.data_arr = self.remove_repeated_ids()
        self.dict_data = self.createMostRecentSN(data)
        self.ids_data = self.repeatedSNForExpansion()
        self.start = start
        self.end = end
        self.dAsys = DataAnalysis(self.data_arr)
        self.error_count = self.dAsys.get_error_count(self.dict_data)
        self.expanded = set()
        self.current_sort_order = {"Fail/Pass Current Status": 'asc', "Step ID": 'asc', "Date first tested": 'asc',
                                   "Error Type": 'asc'}
        self.create_widgets()

    def create_widgets(self):
        tab_control = ttk.Notebook(self)

        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)
        tab3 = ttk.Frame(tab_control)
        tab4 = ttk.Frame(tab_control)

        # Add tabs to the notebook
        tab_control.add(tab1, text='Serial Information')
        tab_control.add(tab2, text='Error Percentage')
        tab_control.add(tab3, text='Final Table')
        tab_control.add(tab4, text='User Information')

        tab_control.pack(expand=1, fill='both')  # Pack the notebook to expand and fill the available space

        # TAB 1

        # Make the frame
        frame_tab1 = tk.Frame(tab1)
        frame_tab1.pack(pady=10)

        # Label
        serial_label = ttk.Label(frame_tab1, text="Enter Serial Number:")
        serial_label.grid(row=0, column=0, padx=5)

        # Entry Box
        self.serial_number_entry = ttk.Entry(frame_tab1, width=20)
        self.serial_number_entry.grid(row=0, column=1, padx=5)

        # Get Information Button
        self.get_info_button = ttk.Button(frame_tab1, text="Get Information", command=self.get_serial_info)
        self.get_info_button.grid(row=0, column=2, padx=5)

        # Create the table
        self.tab1_tree_view = ttk.Treeview(tab1)
        self.tab1_tree_view["columns"] = ("ID", "Test Date", "Unit Status", "Error Type")
        for col in self.tab1_tree_view["columns"]:
            self.tab1_tree_view.heading(col, text=col, anchor=tk.CENTER)
            self.tab1_tree_view.column(col, anchor=tk.CENTER)

        # Fill the space with the specific components
        self.tab1_tree_view.pack(fill="both", expand=True)

        # TAB 2
        # Create the frame
        frame2 = tk.Frame(tab2)
        frame2.pack(pady=10, fill="both")

        # Create the table
        self.tab2_tree_view = ttk.Treeview(tab2)
        self.tab2_tree_view["columns"] = ("Error Type", "Units")
        for col in self.tab2_tree_view["columns"]:
            self.tab2_tree_view.heading(col, text=col, anchor=tk.CENTER)
            self.tab2_tree_view.column(col, anchor=tk.CENTER)

        # Delete old entries and insert new entries from the error count list
        self.tab2_tree_view.delete(*self.tab2_tree_view.get_children())
        for row in self.error_count:
            self.tab2_tree_view.insert('', 'end', values=row)

        # Create the statistics label
        self.statistics_label_tab2 = ttk.Label(frame2, text="Statistics: ")
        self.statistics_label_tab2.config(font=('Segoe UI', 12))  # Set the font using the config method
        self.statistics_label_tab2.grid(row=2, column=4, columnspan=5, padx=5, pady=10, sticky="n")

        # Calculate the statistics for display
        total_count = sum([float(item[1]) for item in self.error_count])
        largest_fail_name = max(self.error_count, key=lambda x: float(x[1]))[0]

        # Populate the statistics label
        self.statistics_label_tab2.config(
            text=f"Highest Error: {largest_fail_name} | Failed Units: {total_count}")  # Update the statistics label

        # Fill the entire window with components
        self.tab2_tree_view.pack(fill="both", expand=True)

        # TAB 3
        # Create the frame
        frame_tab3 = ttk.Frame(tab3)
        self.tab3_tree_view = ttk.Treeview(tab3)

        # Create a vertical scrollbar for tab3_tree_view
        scrollbar = tk.Scrollbar(frame_tab3, orient="vertical", command=self.tab3_tree_view.yview)
        scrollbar.pack(side="right", fill="y")
        self.tab3_tree_view.configure(yscrollcommand=scrollbar.set)

        # Download .csv button
        download_button = tk.Button(frame_tab3, text="Download .csv", command=self.download_csv)
        download_button.pack(side=tk.TOP, anchor='w', padx=5, pady=5)  # Pack the button to the top

        # Create a tree view
        self.tab3_tree_view = ttk.Treeview(frame_tab3, yscrollcommand=scrollbar.set)
        self.tab3_tree_view["columns"] = ("Fail/Pass Current Status", "Step ID", "Date first tested", "Error Type")

        # Create the table
        for col in self.tab3_tree_view["columns"]:
            self.tab3_tree_view.heading(col, text=col, anchor=tk.CENTER,
                                        command=lambda c=col: self.sort_treeview(self.tab3_tree_view, c))
            self.tab3_tree_view.column(col, anchor=tk.CENTER)

        # Fill the tabel and scroll bar to fit the screen
        self.tab3_tree_view.pack(fill="both", expand=True)

        # Populate the table
        for item in self.dict_data:
            item_id = self.tab3_tree_view.insert("", "end", text=item['serial_number'],
                                                 values=(item['status'], '', item['date_tested']))
            self.tab3_tree_view.insert(item_id, 'end', text='Details: ', values=("", "", ""), open=False)

        # Fill components to fit the screen again
        self.tab3_tree_view.pack(fill="both", expand=True)

        # Add a tag to identify the ID rows
        self.tab3_tree_view.tag_configure('id_tag', background='light blue')

        # Bind events
        self.tab3_tree_view.bind("<ButtonRelease-1>",
                                 self.show_instances)  # Bind single click event to show instances
        self.tab3_tree_view.bind("<Double-ButtonRelease-1>",
                                 self.open_html_file)  # Bind double click event to open HTML file

        # Make the statistics label
        self.statistics_label_tab3 = ttk.Label(tab3, text="Statistics: ")
        self.statistics_label_tab3.config(font=('Segoe UI', 12))  # Set the font using the config method
        self.statistics_label_tab3.pack(side=tk.TOP, anchor='w', padx=5, pady=5)
        final_table = []
        for item in self.dict_data:
            final_table.append(item['status'])

        # Calculate and fill the statistics label
        total_units = len(final_table)
        passed_units = sum(1 for row in final_table if row == 'Pass')
        failed_units = sum(1 for row in final_table if row == 'Fail')
        percent_passed = (passed_units / total_units) * 100
        percent_failed = (failed_units / total_units) * 100
        self.statistics_label_tab3.config(
            text=f"Statistics: Percent Passed: {percent_passed:.2f}% | Percent Failed: {percent_failed:.2f}% | Total Units: {total_units}")

        # Pack frame_tab3 after creating and configuring the tree view
        frame_tab3.pack(expand=True, fill='both')

        # TAB 4
        # Create the frame
        frame4 = tk.Frame(tab2)
        frame4.pack(pady=10, fill="both")

        # Create the table
        self.tab4_tree_view = ttk.Treeview(tab4)
        self.tab4_tree_view["columns"] = ("Username", "Average Time Between Tests")

        # Create the table
        for col in self.tab3_tree_view["columns"]:
            self.tab3_tree_view.heading(col, text=col, anchor=tk.CENTER,
                                        command=lambda c=col: self.sort_treeview(self.tab4_tree_view, c))
            self.tab3_tree_view.column(col, anchor=tk.CENTER)

        # Delete old entries and insert new entries from the error count list
        self.tab4_tree_view.delete(*self.tab4_tree_view.get_children())
        for row in self.error_count:
            self.tab4_tree_view.insert('', 'end', values=row)

   # Fill the entire window with components
        self.tab4_tree_view.pack(fill="both", expand=True)


    def remove_repeated_ids(self):
        """
        Removes rows with repeated IDs from the input array.

        Returns:
            list: A list containing unique rows based on the first element (ID) of each row.
        """
        data = self.input_arr
        seen_ids = set()
        result = []

        for row in data:
            current_id = row[0]
            if current_id not in seen_ids:
                result.append(row)
                seen_ids.add(current_id)

        return result

    def createMostRecentSN(self, data):
        """
        Cleans data by keeping only the most recent entry for each serial number.

        Args:
            data (list): Input data to be cleaned.

        Returns:
            list: A list containing the most recent entry for each serial number.
        """
        input_data = data
        output_data = {}

        # Iterate through the input data and keep only the most recent entry for each serial number
        for item in input_data:
            serial_number = item[1]
            status = 'Pass' if item[3].lower() == 'passed' else 'Fail'
            date_tested = item[2]
            error = item[4]

            # Check if the serial number is already in the output_data dictionary
            if serial_number not in output_data or date_tested > output_data[serial_number]['date_tested']:
                # If it's not in the dictionary or the current entry has a more recent date, update the dictionary
                output_data[serial_number] = {'serial_number': f'{serial_number.zfill(3)}', 'status': status,
                                              'date_tested': date_tested, 'error_type': error}

        # Convert the dictionary values to a list to match the original output format
        cleaned_data = list(output_data.values())

        return cleaned_data

    def repeatedSNForExpansion(self):
        """
                Prepares data for expansion which is when the + button is hit, creating a list of dictionaries with all SN instances.

                Returns:
                    list: A list containing dictionaries with information for test run.
        """
        input_data = self.data_arr
        ids_data = []

        # Create the dictionary
        for item in input_data:
            serial_number = item[1]
            status = 'Pass' if item[3].lower() == 'passed' else 'Fail'
            error_type = item[4]
            date_tested = item[2]
            id = item[0]

            id_number = f'{id}'
            html_file = 'none'

            ids_data.append(
                {'serial_number': serial_number, 'id': id_number, 'date_tested': date_tested, 'status': status,
                 'error_type': error_type, 'html_file': html_file})
        return ids_data

    def get_serial_info(self):
        """
        Retrieves serial information based on a provided serial number.

        Updates:
            Modifies the tab1_tree_view widget with the retrieved serial information.
        """
        # Getting the information on a SN
        serial_number = self.serial_number_entry.get()
        SN_Arr = self.dAsys.get_serial_info(serial_number)

        # Error box or fills the data
        if not SN_Arr:
            messagebox.showerror("Error", "Error: No serial number in the specified date range")
        else:
            self.tab1_tree_view.delete(*self.tab1_tree_view.get_children())
            for row in SN_Arr:
                self.tab1_tree_view.insert('', 'end', values=row)

    def open_html_file(self, event):
        """
        Opens the HTML file associated with the clicked ID in the default web browser.

        Args:
            event: The event that triggered the method is a double click on a highlighted row

        Returns:
            None

        Behavior:
            - Retrieves the selected item ID and text from the tab3_tree_view widget.
            - Checks if the double-clicked item is a leaf node (an ID row) based on the 'id_tag' tag.
            - If the item is an ID row:
                - Displays an information message indicating that the file system search may take some time.
                - Finds the clicked ID's HTML file path using the getFilePath method.
                - Opens the HTML file in the default web browser.
        """
        item_id = self.tab3_tree_view.focus()
        item_text = self.tab3_tree_view.item(item_id)['text']

        # Check if the double-clicked item is a leaf node (an ID row)
        if self.tab3_tree_view.tag_has('id_tag', item_id):
            messagebox.showinfo("Loading HTML File", "Searching the file system may take up to a minute. Press OK to start")

            # Find the clicked ID's HTML file path
            for id_info in self.ids_data:
                if id_info['serial_number'] == item_text.split()[0]:
                    html_file_path, length = self.getFilePath(item_text)

                    # Open the HTML file in the default web browser
                    def open_network_folder(folder_path):
                        try:
                            subprocess.run(["explorer", f'{html_file_path[0]}'], check=True)
                        except subprocess.CalledProcessError as e:
                            print(f"Error: {e}")

                    # Replace '\\network\\folder' with the actual network folder path you want to open
                    open_network_folder('\\\\network\\folder')
                    break
    def show_instances(self, event):
        """
        In short this function handles the expansion when hitting a + button on a row.

        Displays instances related to the selected serial number in the tab3_tree_view widget.

        Args:
            event: The event that triggered the method which in this case is a single click on the plus button

        Behavior:
            - Retrieves the selected item ID from the tab3_tree_view widget.
            - Checks if an item is selected.
            - If an item is selected and not already expanded:
                - Removes existing child items under the selected item.
                - Inserts instances as child items based on the serial number from self.ids_data.
                - Updates the expanded set to track expanded items.

        Note:
            The method is used as an event handler for a user action.
        """
        item_id = self.tab3_tree_view.focus()

        # Check if an item is selected
        if item_id:
            item_text = self.tab3_tree_view.item(item_id)['text']

            # If the item is not already expanded
            if item_text not in self.expanded:
                # Remove existing child items
                for child in self.tab3_tree_view.get_children(item_id):
                    self.tab3_tree_view.delete(child)
                # Insert instances as child items
                for id_info in self.ids_data:
                    if id_info['serial_number'] == item_text:
                        id_item = id_info['id']
                        status = id_info['status']
                        SN = id_info['serial_number']
                        date_tested = id_info['date_tested']
                        error_type = id_info['error_type']

                        self.tab3_tree_view.insert(item_id, 'end', text=SN + " " + date_tested,
                                                   values=(status, id_item, date_tested, error_type), tags=('id_tag',))

                # Update the expanded set
                self.expanded.add(item_text)

    def download_csv(self):
        """
        Downloads unexpanded rows data to a CSV file.

        Returns:
            None

        Behavior:
            - Prompts the user to choose a file path for saving the CSV file.
            - If a valid file path is provided:
                - Opens the file in write mode and creates a CSV writer.
                - Writes the header row with column names: ["Serial Number", "Status", "Date Tested"].
                - Iterates through unexpanded rows in self.dict_data:
                    - Extracts relevant information: serial_number, status, and date_tested.
                    - Writes a row to the CSV file.
        """
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
                                                 initialfile=f"CTS_Statistics_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
        if file_path:
            with open(file_path, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["Serial Number", "Status", "Date Tested"])
                for item in self.dict_data:
                    time_data = item['date_tested'].split('.')[0]
                    csv_writer.writerow(
                        [item['serial_number'], item['status'], datetime.strptime(time_data, "%Y-%m-%d %H:%M:%S")])

    def getFilePath(self, serial_number):
        """
                Retrieves file paths associated with a given serial number and its corresponding date.

                Args:
                    serial_number (str): The serial number in the format 'SerialNumber Date Time'.

                Returns:
                    tuple: A tuple containing a list of matching file paths and the number of matching files.

                Example:
                    getFilePath('123456 2022-01-01 12:30:45')  # Returns (['path/to/file1.txt', 'path/to/file2.txt'], 2)
        """

        text = serial_number.split()
        serial_number = text[0]
        date_part = text[1] + " " + text[2].split('.')[0]

        # Convert the date string from the serial number to a datetime object
        serial_date = datetime.strptime(date_part, '%Y-%m-%d %H:%M:%S')
        serial_date_final = serial_date.strftime('[%I %M %S %p][%m %d %Y]')
        print(serial_date)
        print(serial_date_final)
        month = serial_date.strftime('%m')
        year = serial_date.strftime('%Y')
        print(year)

        search_current = False
        # Sets a path and parses the data
        folder_path = "P:\\Quality Systems\\Test Engineering\\Test Equipment\\Common Test System\\CurrentLogTemp"
        backup_path = f"P:\\Quality Systems\\Test Engineering\\Test Equipment\\Common Test System\\Logs\\{year}\\{month}"
        if os.path.exists(backup_path):
            folder_path = backup_path
            search_current = True
        print(folder_path)

        # Iterate through all files in the specified folder
        pattern = os.path.join(folder_path, f"*{serial_number}*{serial_date_final}*")
        matching_files = [file for file in glob.glob(pattern, recursive=True) if os.path.isfile(file)]

        if matching_files == [] and search_current:
            # Iterate through all files in the specified folder
            folder_path = "P:\\Quality Systems\\Test Engineering\\Test Equipment\\Common Test System\\CurrentLogTemp"
            pattern = os.path.join(folder_path, f"*{serial_number}*{serial_date_final}*")
            matching_files = [file for file in glob.glob(pattern, recursive=True) if os.path.isfile(file)]

        return matching_files, len(matching_files)

    def sort_treeview(self, tree_view, column):
        """
        Sorts the treeview based on the specified column.

        Args:
            tree_view: The tkinter treeview widget to be sorted.
            column: The column index by which to sort the treeview.
        """
        # Get the current sort order for the column
        sort_order = self.current_sort_order[column]

        # Change the sort order for the next click
        self.current_sort_order[column] = 'desc' if sort_order == 'asc' else 'asc'

        # Get all items and their values for the specified column
        current_items = [(tree_view.set(item, column), item) for item in tree_view.get_children("")]
        # Sort the items based on the values and sort order
        current_items.sort(reverse=(sort_order == 'desc'))

        # Rearrange the items in the treeview
        for index, (value, item) in enumerate(current_items):
            tree_view.move(item, "", index)
