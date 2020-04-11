import base64
import csv
import os
import os.path
import pickle
import random
import re
import sys
import time
from datetime import datetime
from os import path
import database_writer  # database_writer file

import numpy as np
# BeautifulSoup imports
from bs4 import BeautifulSoup
# Selenium imports
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


# Save increment counter to file to be recovered after system reopened
def save_options(number_to_save):
    w = open("incrementer.txt", "w")
    w.write(str(number_to_save))


# This method encodes title and description into base64 to preserve line breaks
# and special characters.
# It also solves the problem of csv writer defaulting ',' as "new row" delimiter
def write_row(number, title, description, category, answer):
    global database
    q_answeredtf = '0'  # write False to CSV file --> not answered
    if not database:
        try:
            encoded_title = base64.b64encode(title.encode())
            # Otherwise encode the full description
            encoded_description = base64.b64encode(description.encode())

            if answer == "":
                encoded_answer = ""
            else:
                encoded_answer = base64.b64encode(answer.encode())
                q_answeredtf = '1'  # Otherwise the question is answered

            string_var = [number, encoded_title, encoded_description, category, encoded_answer, q_answeredtf]

            csv_writer(string_var, number)  # number = q_number

        except PermissionError:
            print('Document open, cannot write. Now sleeping for 15 seconds')
            a = 15
            while a != 0:
                print(a)
                time.sleep(1)
                a = a - 1
    else:  # elif write to database is true
        if answer != "":
            q_answeredtf = '1'  # Otherwise the question is answered

        dbw = database_writer
        dbw.set_values_to_import(description, number, title, category, q_answeredtf, answer)
        dbw.main()  # Execute write


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
def csv_writer(string_var, q_number):
    # List to hold values for write_row
    # csv columns  # for DictWriter headers
    my_fields = ['number', 'title', 'description', 'category', 'answer-body', 'answered-tf']

    q_number = int(q_number)
    my_file = open('export/questions.csv', 'a')
    write = csv.DictWriter(my_file, fieldnames=my_fields, lineterminator='\n')

    if q_number <= 1 or os.stat("export/questions.csv").st_size == 0:
        write.writeheader()

    write.writerow({'number': f'{string_var[0]}', 'title': f'{string_var[1]}', 'description': f'{string_var[2]}',
                    'category': f'{string_var[3]}', 'answer-body': f'{string_var[4]}',
                    'answered-tf': f'{string_var[5]}'})


def set_options(opt_sign_in):
    global chrome_browser
    global rules
    rules = "umatrix/scraping-rules.txt"
    # Perform all functions required to gather the html of a page while avoiding bot detection
    # Must be outside 'collect_page()' so that a new instance is not created for each iteration
    opts = Options()
    # opts.add_argument("user-agent='Mozilla/5.0 (compatible; GoogleDocs; apps-spreadsheets; +http://docs.google.com)'")
    # opts.add_argument("user-agent=" + "'" + ua.chrome + "'")
    opts.add_argument("--window-size=320,200")
    opts.add_extension("umatrix/extension_1_4_0_0.crx")
    browser = webdriver.Chrome(options=opts, executable_path=new_os_input)
    chrome_browser = browser
    # If the user selected the sign on attempt
    umatrix_rule_set(opt_sign_in, chrome_browser)  # Set the umatrix rule list depending on login


def umatrix_rule_set(umtrx_sign_in, umtrx_chrome_browser):
    # Set uMatrix session settings
    # Navigate to uMatrix session settings page
    umtrx_chrome_browser.get("chrome-extension://ogfcmafjalglgifnmanfmnieipoejdcf/dashboard.html#user-rules")
    # switch to iframe to be able to access the user settings
    frame = umtrx_chrome_browser.find_element_by_xpath('/html/body/iframe')
    umtrx_chrome_browser.switch_to.frame(frame)
    # select box to add changes, clear all and import settings
    settings_window = umtrx_chrome_browser.find_element_by_xpath("/html/body/div[2]/div[2]/div/div[3]"
                                                                 "/div/div[5]/div[1]/div/div/div/div[5]")
    settings_window.send_keys(Keys.CONTROL + "a")
    settings_window.send_keys(Keys.DELETE)

    try:
        if umtrx_sign_in:
            w = open("umatrix/login-rules.txt", "r")
            settings_window.send_keys(w.read())
            umtrx_chrome_browser.find_element_by_id("editSaveButton").click()  # save changes
            umtrx_chrome_browser.find_element_by_id("commitButton").click()  # commit changes
            login(umtrx_chrome_browser)
            umatrix_rule_set(False, umtrx_chrome_browser)  # After logging in, set default web scraping list
        else:
            w = open("umatrix/scraping-rules.txt", "r")
            settings_window.send_keys(w.read())
            umtrx_chrome_browser.find_element_by_id("editSaveButton").click()  # save changes
            umtrx_chrome_browser.find_element_by_id("commitButton").click()  # commit changes
    except Exception as e:
        print(e)
        print("Error logging in")
        menu()


# This method is for logging in to chegg to scrape answers if paid account is available
# currently WIP
def login(login_chrome_browser):
    global username
    global password
    username = "patjobri@gmail.com"
    password = "24Jx%hgXLzIr^nr7"
    login_chrome_browser.get("https://www.chegg.com/auth?action=login")  # Login page
    login_chrome_browser.find_element_by_id("emailForSignIn").send_keys(username)
    login_chrome_browser.find_element_by_id("passwordForSignIn").send_keys(password)

    # Element clicks are being intercepted so it needs javascript to work
    element = login_chrome_browser.find_element_by_xpath("//button[starts-with(@type,'submit')]")
    login_chrome_browser.execute_script("arguments[0].click();", element)
    time.sleep(10)


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

        content = chrome_browser.page_source  # grab html from the page
        return content  # method then returns the html content of the page
    except NoSuchElementException:
        print("Failed to implement anti-detection measures; missing element (or recaptcha present)\n")


# For parsing the webpage if the page is q&a
def start_program():
    global x
    global upperbound
    upperbound = 4000000
    q_number = 0
    x = 0

    try:
        inc = check_for_incrementer()  # return the current increment value if it exists
    except FileNotFoundError:
        print("Incrementer file does not exist")
        inc = 0

    question_list = check_for_numberlist()
    # Should reset at the start of each loop
    title_string = ''  # holds question title
    desc_string = ''  # question description
    ans_string = ''  # question answer

    try:
        # current_question = read_increment_to_use()  # find a random question to scrape (no duplicates)
        for x in range(inc, upperbound):
            q_number = question_list[x]  # assign list question_list the increment [1++] to be question number

            time.sleep(random.randint(2, 3))
            # page = urlopen(req).read()  # take request and read
            soup = BeautifulSoup(collect_page(q_number), 'html.parser')  # parse request to html

            # save counter each loop in event of error/crash
            save_options(x)

            # Find the question title
            if soup.select('h1[class*="PageHeading-"]') or \
                    soup.select('span[class*="question-text question-header-span"]'):  # if the page is a q&a page

                # select the title
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
                    if desc_string is None:
                        # Gather contents of div
                        for row in soup.select('div[class*="Transcript__TranscriptContent-sc-"]'):
                            row = row.text  # Remove html
                            if row is None:  # If the div does not exist
                                row = ""  # Declare row to be empty
                            elif row == "Show transcribed image text":  # Otherwise if the div only contains
                                row = ""  # Remove that value
                            desc_string = row
                    else:  # otherwise,
                        for row in soup.select('div[class*="Transcript__TranscriptContent-sc-"]'):
                            row = row.text  # Remove html
                            if row == "Show transcribed image text":
                                row = ""
                            desc_string += row

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
                # Fill the csv file with the gathered title, description, and category

                # answer_present = False
                # # Check to see if the answer is on the page, if it is record it and add it to the writerow
                # if soup.select('div[class*="txt-body answer-body"]'):
                #     answer_present = True
                #     print("answer is present")
                #     for row in soup.find_all('div[class*="txt-body answer-body"]'):
                #         row = row.text
                #         print("appending answer row.text to ans_string")
                #         ans_string += row.text
                # else:
                #     print("not answered or not logged in")
                #     ans_string = ""  # not answered or not logged in

                # if answer_present:
                #     images = []
                #     print("Locating image")
                #     for img in soup.find_all('img'):
                #         img_src = img.get('src')
                #         match = re.search(r'(https:\/\/media.cheggcdn.com\/study\/(.*))', img_src)
                #         if match.group(1) is not None:
                #             images.append(match.group(1))

                # Remove "Show transcribed image text" from front of transcription description
                match = re.search(r'(Show.transcribed.image.text)', desc_string)
                if match is not None:
                    if match.group(1):
                        # Replace match with empty string
                        desc_string = re.sub(match.group(1), '', desc_string)

                print("Question found! Writing to row")
                write_row(str(q_number), title_string, desc_string, category, ans_string)

                # reset
                title_string = ''  # holds question title
                desc_string = ''  # question description
                ans_string = ''  # question answer

            else:  # Otherwise move to the next function
                pass
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)
        # Export error log to file
        m = open("export/error_log.txt", "a")
        save_options(x)
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
        print(e)
        a = 15
        while a != 0:
            print(a)
            time.sleep(1)
            a = a - 1


# Menu for selecting which driver to use
def menu():
    # Incrementer for keeping track of position in list
    global incrementer  # set to 0
    global x  # Counter value in start_program(), set to 0
    global upperbound
    global sign_in  # login at start T/F
    global username
    global password
    global database
    sign_in = False
    database = True

    print("************WELCOME TO CHEGGSCRAPER************")
    print()
    choice = input("""
     1: Start program
     2: Sign in at start
     3: Manually set x counter position
     4: Set total number of questions to scrape
     5: Set Operating System
     6: Write to csv file or sqlite database
     Q: Quit
     """)
    # Starting the program
    if choice == '1':
        try:
            set_options(sign_in)
            start_program()
            # Exception writes error to a file and saves the question on error
            # for later reference
        except Exception as e:
            print("Error starting program")
            print(e)

    elif choice == '2':
        a = input("Attempt sign in when starting program? (Y/n) ")
        if a == "Y" or a == "y":
            sign_in = True
            a = input("Enter username: ")
            username = a
            a = input("Enter your password: ")
            password = a
            print("Set to true")
            menu()
        elif a == "N" or a == "n":
            sign_in = False
            print("Set to false")
            menu()

    # Manually setting the x-counter position
    elif choice == '3':
        try:
            num_to_save = input("Enter the new increment value: ")
            save_options(num_to_save)
            print("Set " + num_to_save + " to current counter")
            menu()
        except ValueError as e:
            print("Please enter an integer 0-10000000")
            print(e)
            menu()
    # Selecting the operating system specific driver
    elif choice == '4':
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
    # Setting the total number of questions to scrape
    elif choice == '5':
        choice = input("Enter total # of questions: ")
        upperbound = choice
    # Quitting the program
    elif choice == '6':
        choice = input(" 1. Write to csv file \n" + "2. Write to database (default)\n")
        if choice == "1":
            database = False
        else:
            database = True

    elif choice == "Q" or choice == "q":
        sys.exit()
    else:
        print("Error - Select one of the options")
        print("Enter again")
        menu()


# Called once at the start of program to check if numberlist exists
# If the numberlist does not exist, generate the numberlist
# Otherwise, read from the existing numberlist
def check_for_numberlist():
    # If the path doesn't exist, or file empty --> call generate a range of random numbers
    if not path.exists("export/numberlist.data") or os.stat("export/numberlist.data").st_size == 0:
        generate_num_range()
        print("***generated list***")
        menu()
    else:
        question_list = read_next_question_list()  # instance access for random number list
        return question_list


def check_for_incrementer():
    # Load previous iteration if it exists
    if path.exists("incrementer.txt") and os.stat("incrementer.txt").st_size != 0:
        m = open("incrementer.txt", "r")
        inc = int(m.readline())  # read the line - c
        m.close()
        return inc  # return incrementer


# Retrieve the last of numbers
# Returns a list with the 4 million different numbers
def read_next_question_list():
    with open('export/numberlist.data', 'rb') as file_handle:
        # read the data as binary data stream
        number_list = pickle.load(file_handle)
    return number_list


# # Load incrementer file number from previous session on first run if counter file exists
# If the path exists and file is not empty
def generate_num_range():
    ls = np.random.permutation(4000000)
    with open('export/numberlist.data', 'wb') as file_handle:
        # store the data as binary data stream
        pickle.dump(ls, file_handle)


if __name__ == '__main__':
    # Set default operating system at start to windows
    set_os('drivers/chromedriver_windows64/chromedriver.exe')
    menu()
