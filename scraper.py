import base64
import csv
import os.path
import pickle
import random
import re
import sys
import time
from datetime import datetime
from os import path

import numpy as np
# BeautifulSoup imports
from bs4 import BeautifulSoup
# Selenium imports
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options


# Run program
def main():
    menu()


# Save increment counter to file to be recovered after system reopened
def save_counter(number_to_save):
    w = open("incrementer.txt", "w")
    w.write(str(number_to_save))


# This method encodes title and description into base64 to preserve line breaks
# and special characters.
# It also solves the problem of csv writer defaulting ',' as "new row" delimiter
def write_row(number, title, description, category, q_number):
    print(number + title + description + category)
    encoded_title = base64.b64encode(title.encode())
    encoded_description = base64.b64encode(description.encode())

    string_var = [number, encoded_title, encoded_description, category]
    writer(string_var, number)  # number = q_number


# List to hold values for write_row
my_fields = ['number', 'title', 'description', 'category']  # csv columns  # for DictWriter headers


# Set the string value for the operating system to be used
def set_os(os_input):
    global new_os_input
    new_os_input = os_input
    print("New OS set to: " + new_os_input)


# This method writes or appends to the csv file using
# question number: question number from random number list
# title: encoded in base64, first 15 or so characters of description
# description: encoded in base64
# question category ie. 'Physics'
def writer(string_var, q_number):
    my_file = open('export/questions.csv', 'a')
    write = csv.DictWriter(my_file, fieldnames=my_fields)

    if q_number <= 1 or os.stat("export/questions.csv").st_size == 0:
        write.writeheader()

    write.writerow({'number': f'{string_var[0]}', 'title': f'{string_var[1]}', 'description': f'{string_var[2]}',
                    'category': f'{string_var[3]}'})


def set_options():
    global chrome_browser
    # Perform all functions required to gather the html of a page while avoiding bot detection
    # Must be outside 'collect_page()' so that a new instance is not created for each iteration
    opts = Options()
    opts.add_argument("Mozilla/5.0 (compatible; GoogleDocs; apps-spreadsheets; +http://docs.google.com)")
    opts.add_argument("--window-size=320,200")
    opts.add_extension("umatrix/extension_1_4_0_0.crx")
    browser = webdriver.Chrome(options=opts, executable_path=new_os_input)
    chrome_browser = browser


# This method uses selenium to extract the html from the page and preserve the session cookies
def collect_page(q_number):
    try:
        # Setting the user agent
        # Sets the user agent for functions in collect_page(), which is called in the primary loop.

        # Disguise the request as google IP range service
        # User-Agent': 'Mozilla/5.0 (compatible; GoogleDocs; apps-spreadsheets; +http://docs.google.com)
        # Run through all questions in archive by using q###### schema
        # https://www.chegg.com/homework-help/questions-and-answers/q
        # url = "https://cforcomputer.github.io"

        url = 'https://www.chegg.com/homework-help/questions-and-answers/q' + str(q_number)  # Define URL
        chrome_browser.get(url)  # the url
        print(str(x) + " - Scraping: " + url)
        time.sleep(random.uniform(0.5, 1))

        content = chrome_browser.page_source  # grab html from the page
        return content  # method then returns the html content of the page
    except NoSuchElementException:
        print("Failed to implement anti-detection measures; missing element (or recaptcha present)\n")


def start_program():
    question_list = check_for_numberlist()
    # Should reset at the start of each loop
    title_string = ''
    desc_string = ''
    temp_string_array = []  # holds the final output values written to questions.csv
    # current_question = read_increment_to_use()  # find a random question to scrape (no duplicates)
    q_number = question_list[x]  # assign list question_list the increment [1++] to be question number

    # page = urlopen(req).read()  # take request and read
    soup = BeautifulSoup(collect_page(q_number), 'html.parser')  # parse request to html

    # save counter each loop in event of error/crash
    save_counter(x)

    # Find the question title
    if soup.select('h1[class*="PageHeading-"]'):  # if the page is a q&a page

        for EachTitle in soup.select('h1[class*="PageHeading-"]'):
            # Concat. each separate string to fill one row
            title_string += EachTitle.get_text(strip=True)

        # Find the full question text
        for EachDescription in soup.select('section[class*="QuestionBody__QuestionBodyWrapper-sc-"]'):
            # Concat. each separate string to fill one row
            desc_string += EachDescription.get_text(strip=True)

        # Prototyping finding the transcript script
        # Appends the transcribed image text to the end of the description
        if soup.select('div[class*="Transcript__TranscriptContent-sc-"]'):
            desc_string += soup.find('div[class*="Transcript__TranscriptContent-sc-"]')

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
        category = match.group(1)  # remove quotes

        print(q_number + title_string + desc_string + category)
        # Fill the csv file with the gathered title, description, and category
        write_row(q_number, title_string, desc_string, category)

    else:  # Otherwise move to the next function
        pass


# Menu for selecting which driver to use
def menu():
    # global new_os_input
    # Number that stores the current question number being scraped
    # global q_number  # set to 0
    # Incrementer for keeping track of position in list
    global incrementer  # set to 0
    # Counter value in start_program()
    global x  # set to 0

    # Set default operating system at start to windows
    set_os('drivers/chromedriver_windows64/chromedriver.exe')
    try:
        incrementer = check_for_incrementer()  # return the current increment value if it exists
    except FileNotFoundError:
        print("Incrementer file does not exist")
        incrementer = 0
    q_number = 0
    x = 0

    print("************WELCOME TO CHEGGSCRAPER************")
    print()
    choice = input("""
     S: Start program
     B: Manually set x counter position
     M: Set Operating System
     Q: Quit
     """)
    if choice == "S" or choice == "s":
        # Run through every page in the database and store url to text file
        for x in range(incrementer, 4000000):
            try:
                set_options()
                start_program()
                # Exception writes error to a file and saves the question on error
                # for later reference
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(e, exc_type, fname, exc_tb.tb_lineno)
                # Export error log to file
                m = open("export/error_log.txt", "a")
                save_counter(x)
                m.write(str(e))
                m.write('\n')
                m.write('\n')
                m.write("@" + str(datetime.now()))
                m.write('\n')
                m.write("Iteration interrupted at question: " + str(q_number))
                m.close()
                # Wait between 8 and 9 minutes if blocked
                time.sleep(random.randint(200, 400))
                pass
            except PermissionError as e:
                print('Permission Error, now sleeping for 15 seconds')
                a = 15
                while a != 0:
                    print(a)
                    time.sleep(1)
                    a = a - 1

    elif choice == "B" or choice == "b":
        try:
            num_to_save = input("Enter the new increment value: ")
            save_counter(num_to_save)
            print("Saved " + num_to_save + " to file")
            menu()
        except ValueError as e:
            print("Please enter an integer 0-10000000")
            menu()

    elif choice == "M" or choice == "m":
        choice = input("Please select operating environment\n"
                       "Type the number to select\n"
                       "1. (default) Windows\n"
                       "2. Linux\n")

        if choice == "1":
            set_os("drivers/chromedriver_windows64/chromedriver.exe")
        elif choice == "2":
            set_os("drivers/chromedriver_linux64_81/chromedriver")
        else:
            menu()
    elif choice == "Q" or choice == "q":
        sys.exit()
    else:
        print("Error - Select one of the options")
        print("Enter again")
        menu()


# should be called once when the program runs
# Checks to see if numberlist.data exists, if it does, then set question_list to the
# return value of read_next_question_list
def check_for_numberlist():
    # If the path doesn't exist, or file empty --> call generate a range of random numbers
    #
    if not path.exists("export/numberlist.data") or os.stat("export/numberlist.data").st_size == 0:
        generate_num_range()
        print("***generated list***")
        menu()
    else:
        print("Reading existing list")
        question_list = read_next_question_list()  # instance access for random number list
        return question_list


def check_for_incrementer():
    # Load previous iteration if it exists
    if path.exists("incrementer.txt") and os.stat("incrementer.txt").st_size != 0:
        m = open("incrementer.txt", "r")
        incrementer = int(m.readline())  # read the line - c
        m.close()
        return incrementer


# Retrieve the last of numbers
# Returns a list with the 4 million different numbers
def read_next_question_list():
    with open('export/numberlist.data', 'rb') as filehandle:
        # read the data as binary data stream
        number_list = pickle.load(filehandle)
    return number_list


# # Load incrementer file number from previous session on first run if counter file exists
# If the path exists and file is not empty
def generate_num_range():
    ls = np.random.permutation(4000000)
    with open('export/numberlist.data', 'wb') as filehandle:
        # store the data as binary data stream
        pickle.dump(ls, filehandle)


if __name__ == '__main__':
    main()
