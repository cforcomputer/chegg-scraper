import base64
import csv
import os
import random
import sys
import time
import atexit
from datetime import datetime
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
import pandas as pd  # empty file check


# Check to see if the counter value is present and in the text file before continuing
def load_counter():
    try:
        global incrementer
        w = open("incrementer.txt", "r")
        temp = int(w.readline())
        if temp > 0:
            incrementer = temp
    except FileNotFoundError:
        print("Beginning first run")
        incrementer = 0
    return incrementer


# Save increment counter to file to be recovered after system reopened
def save_counter():
    w = open("incrementer.txt", "w")
    w.write(str(incrementer))


def create_row(number, title, description, category):
    encoded_title = base64.b64encode(title.encode())
    encoded_description = base64.b64encode(description.encode())

    string_var = [number, encoded_title, encoded_description, category]
    writer(string_var)


# Helper function for writing to file
my_fields = ['number', 'title', 'description', 'category']  # csv columns  # for DictWriter headers


def writer(string_var):
    my_file = open('export/questions.csv', 'a')
    df = pd.read_csv('export/questions.csv')
    write = csv.DictWriter(my_file, fieldnames=my_fields)

    if incrementer <= 1 or df.empty:
        write.writeheader()

    write.writerow({'number': f'{string_var[0]}', 'title': f'{string_var[1]}', 'description': f'{string_var[2]}',
                    'category': f'{string_var[3]}'})


# Load incrementer file number from previous session on first run if counter file exists
incrementer = load_counter()

# Run through every page in the database and store url to text file
for x in range(incrementer, 10):
    # Should reset at the start of each loop
    title_string = ''
    desc_string = ''
    temp_string_array = []

    # Run through all questions in archive by using q###### schema
    #
    # url = "http://patspace.me"
    url = "https://www.chegg.com/homework-help/questions-and-answers/q" + str(incrementer)
    incrementer += 1

    # Disguise the request as google IP range service
    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; GoogleDocs; apps-spreadsheets; +http://docs.google.com)',
        "Accept-Language": "en-US, en;q=0.5"
    })
    print(str(x) + " - Scraping: " + url)
    # Reduce suspicion by grabbing page at random intervals
    time.sleep(random.randint(11, 20))

    try:
        page = urlopen(req).read()  # take request and read
        soup = BeautifulSoup(page, 'html.parser')  # parse request to html

        # Find the question title
        if soup.select('h1[class*="PageHeading-"]'):  # if the page is a q&a page

            for EachTitle in soup.select('h1[class*="PageHeading-"]'):
                # Concat. each separate string to fill one row
                title_string += EachTitle.get_text(strip=True)

            # Find the full question text
            for EachDescription in soup.select('section[class*="QuestionBody__QuestionBodyWrapper-sc-"]'):
                # Concat. each separate string to fill one row
                desc_string += EachDescription.get_text(strip=True)

            # Fill the csv file with the gathered title, description, and category
            create_row(x, title_string, desc_string, 'uncategorized')

        else:  # Otherwise move to the next function
            pass
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)
        # Export error log to file
        m = open("export/error_log.txt", "a")
        m.write(str(e))
        m.write('\n')
        m.write("Iteration interrupted at question: " + str(incrementer))
        m.write('\n')
        m.write("@" + str(datetime.now()))
        m.write('\n')
        m.close()
        x = incrementer - 1
        incrementer = x  # start from last stop
        # Wait between 8 and 10 minutes if blocked
        time.sleep(random.randint(800, 1000))
        pass

atexit.register(save_counter)  # At normal program close, save the text file
