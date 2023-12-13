from collections import Counter

# The purpose of this class is to hold data processing methods which are used in handling data to display
# in the tabs_window class
class DataAnalysis:
    def __init__(self, query_output):
        """
        Initializes the DataAnalysis class with the query output.

        Parameters:
        - query_output: List of rows obtained from a database query.
        """
        self.query_output = query_output

    def get_serial_info(self, serial_number):
        """
        Retrieves information from the query output for a given serial number.

        As well as formats the serial number's information for display

        Parameters:
        - serial_number: Serial number to filter the rows.

        Returns:
        - List of matching rows containing elements at indices 0, 2, 3, and 4.
        """
        matching_rows = []
        for row in self.query_output:
            if row[1] in serial_number:
                matching_rows.append([row[0], row[2], row[3], row[4]])
        return matching_rows

    def get_error_count(self, input_arr):
        """
        Counts the occurrences of error types in the given input array and returns the results sorted by count.

        Example: [Sleep Current, 5] which is the error type and the number of occurrences in the dict

        Parameters:
        - input_arr: List of dictionaries representing data rows.

        Returns:
        - List of tuples containing error types and their counts, sorted in descending order of count.
        """
        errors = []
        for row in input_arr:
            if row['status'] == 'Fail':
                if row['error_type'] == "":
                    row['error_type'] = "Terminated"
                errors.append(row['error_type'])
        count_dict = Counter(errors)
        result = [(key, value) for key, value in count_dict.items()]
        sorted_error_count = sorted(result, key=lambda x: float(x[1]), reverse=True)
        return sorted_error_count
