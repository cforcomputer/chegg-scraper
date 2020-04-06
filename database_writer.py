# Writes to database
import sqlite3


def create_connection(db_file):  # db_file = db.sqlite3
    """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn  # return new database connection
