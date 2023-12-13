from database_connector import DatabaseConnector
import time

# This file interacts with database_connector by getting information on the output of the app and creating
# and sending a custom query


# Database connection string this uses the microsoft authentication from your account
conn_str = (
    'DRIVER={SQL Server};'
    'SERVER=NKSQL1\\NKSQL1;'
    'DATABASE=TestStandCustom;'
    'Trusted_Connection=yes;'
)


# This method defines and sends a query to Database Connector
def createQuery(start_date, end_date, program_file):
    # Create a list of parameters for the SQL query
    params = [start_date, end_date]

    # Create an instance of the DatabaseConnector class and connect to the database
    db_connector = DatabaseConnector(conn_str)
    db_connector.connect()

    # SQL query to retrieve information from the database
    # Important notes being Left Join allows for the CASE statement to provide blank STEP_Names
    query = "SELECT DISTINCT dbo.UUT_RESULT.ID, dbo.UUT_RESULT.UUT_SERIAL_NUMBER, dbo.UUT_RESULT.START_DATE_TIME, " \
            "dbo.UUT_RESULT.UUT_STATUS, CASE WHEN dbo.UUT_RESULT.UUT_STATUS = 'failed' THEN " \
            "[View_Failed Top Level UUTs and Results].STEP_NAME ELSE '' END AS STEP_NAME, " \
            "dbo.STEP_RESULT.CAUSED_SEQFAIL, dbo.STEP_RESULT.STEP_TYPE FROM dbo.UUT_RESULT " \
            "LEFT JOIN dbo.STEP_RESULT ON dbo.UUT_RESULT.ID = dbo.STEP_RESULT.UUT_RESULT " \
            "LEFT JOIN dbo.STEP_SEQCALL ON dbo.STEP_RESULT.ID = dbo.STEP_SEQCALL.STEP_RESULT " \
            "LEFT JOIN [TestStandCustom].[dbo].[View_Failed Top Level UUTs and Results] " \
            "ON dbo.[View_Failed Top Level UUTs and Results].UUT_SERIAL_NUMBER = dbo.UUT_RESULT.UUT_SERIAL_NUMBER " \
            "WHERE dbo.UUT_RESULT.START_DATE_TIME BETWEEN ? AND ?"

    # This next if statement adds the words to search for in the program files
    # It uses SQL wild cards to do this
    # Check if "#Multiple_Params" is present in the program_file
    if "#Multiple_Params" in program_file:
        parry = []
        array = program_file.split()[:-1]
        query += " AND (SEQUENCE_FILE_PATH LIKE ?"

        # Add placeholders for each parameter in the array
        for _ in range(len(array) - 1):
            query += " OR SEQUENCE_FILE_PATH LIKE ?"

        # Build parameter values and add them to the params list
        for item in array:
            parry.append("%" + item + "%")
        params += parry
    else:
        query += " AND (SEQUENCE_FILE_PATH LIKE ?"
        program_file = "%" + program_file + "%"
        params.append(program_file)

    query += ") "

    # Print the final query for debugging purposes
    print(query, tuple(params))

    # Measure the execution time of the query
    time_start = time.time()
    data = db_connector.execute_query(query, tuple(params))
    time_end = time.time()

    # Calculate and print the elapsed time
    elapsed_time = round(time_end - time_start)
    print(f"The query took: {elapsed_time} seconds")

    # Strip leading and trailing whitespaces from string values in the result
    for rows in data:
        for i in range(len(rows)):
            if type(rows[i]) == str:
                rows[i] = rows[i].strip()

    # Close the database connection
    db_connector.close()

    # Return the retrieved data
    return data
