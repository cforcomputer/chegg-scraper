import base64
import csv
import os
import random
import re
import sys
import time
import atexit
from datetime import datetime
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


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


def write_row(number, title, description, category):
    encoded_title = base64.b64encode(title.encode())
    encoded_description = base64.b64encode(description.encode())

    string_var = [number, encoded_title, encoded_description, category]
    writer(string_var)


# Helper function for writing to file
my_fields = ['number', 'title', 'description', 'category']  # csv columns  # for DictWriter headers


def writer(string_var):
    my_file = open('export/questions.csv', 'a')
    write = csv.DictWriter(my_file, fieldnames=my_fields)

    if incrementer <= 1 or os.stat("export/questions.csv").st_size == 0:
        write.writeheader()

    write.writerow({'number': f'{string_var[0]}', 'title': f'{string_var[1]}', 'description': f'{string_var[2]}',
                    'category': f'{string_var[3]}'})


# Load incrementer file number from previous session on first run if counter file exists
incrementer = load_counter()

# Run through every page in the database and store url to text file
for x in range(incrementer, 4000000):
    # Should reset at the start of each loop
    title_string = ''
    desc_string = ''
    temp_string_array = []

    # Run through all questions in archive by using q###### schema
    # https://www.chegg.com/homework-help/questions-and-answers/q
    # url = "http://patspace.me"
    url = "https://www.chegg.com/homework-help/questions-and-answers/q" + str(incrementer)
    incrementer += 1

    # Disguise the request as google IP range service
    # User-Agent': 'Mozilla/5.0 (compatible; GoogleDocs; apps-spreadsheets; +http://docs.google.com)
    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; GoogleDocs; apps-spreadsheets; +http://docs.google.com)'
    })
    print(str(x) + " - Scraping: " + url)
    # Reduce suspicion by grabbing page at random intervals
    time.sleep(random.randint(11, 18))

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

            # Add a loop to gather the breadcrumb name of a page
            # results = soup.find(lambda tag: " questions and answers" in tag.string if tag.string else False)
            # Javascript parser for identifying specific breadcrumbs
            # Param result = string containing breadcrumb script
            scripts = soup.find_all("script")
            category = ''
            for script in scripts:
                text = script.text
                m_text = text.split(',')
                for n in m_text:
                    if '"parentSubject":' in n:
                        category = n  # Get subject name from script

            match = re.search(r':"(.*?)"', category)  # Apply regex to grab only second word
            category = match.group(1)
            # Fill the csv file with the gathered title, description, and category
            write_row(x, title_string, desc_string, category)

        else:  # Otherwise move to the next function
            pass
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)
        # Export error log to file
        m = open("export/error_log.txt", "a")
        save_counter()
        m.write(str(e))
        m.write('\n')
        m.write('\n')
        m.write("@" + str(datetime.now()))
        m.write('\n')
        x = incrementer - 1
        incrementer = x  # start from last stop
        m.write("Iteration interrupted at question: " + str(incrementer))
        m.close()
        # Wait between 8 and 9 minutes if blocked
        time.sleep(random.randint(800, 900))
        pass

atexit.register(save_counter)  # At normal program close, save the text file
