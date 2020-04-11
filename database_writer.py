# Writes to database
import sqlite3
import datetime


# Gets the current date and time and returns it in a string
# Same format that django generates
def get_datetime():
    now = datetime.datetime.now()
    return datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)


# Method to create a new function to establish a database connection
# to an SQlite database specified by the database file
def set_values_to_import(question_description, question_number, question_title,
                         question_topic, answered, question_answer):
    global q_description_in, q_number_in, q_title_in, q_topic_in, q_anstf_in, q_answer_text_in
    q_description_in = question_description
    q_number_in = question_number
    q_title_in = question_title
    q_topic_in = question_topic
    q_anstf_in = answered
    q_answer_text_in = question_answer


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


# ORDER:
# id = 1, 2, 245, etc...
# pub_date = 2020-04-06 04:15:31
# question_description = Full description string
# question_number = 1826095
# question_title = Full question title string
# question_topic = Electrical Engineering
# answered = 1 or 0, where 0 = False
# question_answer = NA for Not Answered, or full answer string
# Insert a new question into the questions table
# TODO: Need to implement a check to see if the question already exists in the database
def create_question(conn, task):

    sql = ''' INSERT INTO questions_question(id, pub_date, question_description, question_number,
     question_title, question_topic, answered, question_answer) VALUES(?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, task)
    return cur.lastrowid


def main():
    global q_description_in, q_number_in, q_title_in, q_topic_in, q_anstf_in, q_answer_text_in
    database = r"db.sqlite3"
    q_id_in = q_number_in  # ID same as question number
    q_datetime_in = get_datetime()  # Same published date as django
    # Create connection
    conn = create_connection(database)
    with conn:
        # Create new question
        task = (q_id_in, q_datetime_in, q_description_in, q_number_in,
                  q_title_in, q_topic_in, q_anstf_in,  q_answer_text_in)
        create_question(conn, task)


# Module testing
if __name__ == '__main__':
    # Set default operating system at start to windows
    print(get_datetime())
