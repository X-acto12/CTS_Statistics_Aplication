import pyodbc


class DatabaseConnector:
    """
    A class for connecting to a database and executing queries.

    Attributes:
        conn_str (str): The connection string for the database.
        conn: The database connection object.
        cursor: The cursor object for executing queries.

    Methods:
        connect: Establishes a connection to the database.
        execute_query: Executes a SQL query and returns the results.
        close: Closes the connection to the database.
    """

    def __init__(self, conn_str):
        """
        Initializes a DatabaseConnector instance with the provided connection string.

        Args:
            conn_str (str): The connection string for the database.
        """
        self.conn_str = conn_str
        self.conn = None
        self.cursor = None

    def connect(self):
        """
        Establishes a connection to the database using the provided connection string.
        """
        self.conn = pyodbc.connect(self.conn_str)
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=None):
        """
        Executes the provided SQL query and returns the results.

        Args:
            query (str): The SQL query to be executed.
            params (tuple, optional): The parameters to be used in the query.

        Returns:
            list: A list of rows returned from the executed query.

        Raises:
            Exception: If the connection has not been established, it raises an exception.
        """
        if self.cursor:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows
        else:
            raise Exception("Connection not established. Please connect first.")

    def close(self):
        """
        Closes the connection to the database.
        """
        if self.conn:
            self.conn.close()
        else:
            raise Exception("Connection not established.")
