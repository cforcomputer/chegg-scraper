import atexit
import base64
import csv
import os.path
from os import path
import random
import re
import sys
import time
from datetime import datetime
import math
import pickle

# BeautifulSoup imports
from bs4 import BeautifulSoup
# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.touch_actions import TouchActions
from selenium.common.exceptions import NoSuchElementException


# Return a randomized "range" using a Linear Congruential Generator
# to produce the number sequence. Parameters are the same as for
# python builtin "range".
#   Memory  -- storage for 8 integers, regardless of parameters.
#   Compute -- at most 2*"maximum" steps required to generate sequence.
#
def random_range(start, stop=None, step=None):
    # Set a default values the same way "range" does.
    if stop is None: start, stop = 0, start
    if step is None: step = 1
    # Use a mapping to convert a standard range into the desired range.
    mapping = lambda i: (i * step) + start
    # Compute the number of numbers in this range.
    maximum = (stop - start) // step
    # Seed range with a random integer.
    value = random.randint(0, maximum)
    #
    # Construct an offset, multiplier, and modulus for a linear
    # congruential generator. These generators are cyclic and
    # non-repeating when they maintain the properties:
    #
    #   1) "modulus" and "offset" are relatively prime.
    #   2) ["multiplier" - 1] is divisible by all prime factors of "modulus".
    #   3) ["multiplier" - 1] is divisible by 4 if "modulus" is divisible by 4.
    #
    offset = random.randint(0, maximum) * 2 + 1  # Pick a random odd-valued offset.
    multiplier = 4 * (maximum // 4) + 1  # Pick a multiplier 1 greater than a multiple of 4.
    modulus = int(
        2 ** math.ceil(math.log2(maximum)))  # Pick a modulus just big enough to generate all numbers (power of 2).
    # Track how many random numbers have been returned.
    found = 0
    while found < maximum:
        # If this is a valid value, yield it in generator fashion.
        if value < maximum:
            found += 1
            yield mapping(value)
        # Calculate the next value in the sequence.
        value = (value * multiplier + offset) % modulus


# Calls random range to generate a text file with the psuedo-random order
# The sequence of numbers has no repeats
def generate_num_range():
    li = []
    for v in range(1, 4000000):
        v = 2 ** v
        li = list(random_range(v))
    with open('export/numberlist.data', 'wb') as filehandle:
        # store the data as binary data stream
        pickle.dump(li, filehandle)


# Retrieve the last of numbers
# Returns a list with the 4 million different numbers
def read_next_question_list():
    with open('export/numberlist.data', 'rb') as filehandle:
        # read the data as binary data stream
        number_list = pickle.load(filehandle)
    return number_list


# Save increment counter to file to be recovered after system reopened
def save_counter(number_to_save):
    w = open("incrementer.txt", "w")
    w.write(str(number_to_save))


# This method encodes title and description into base64 to preserve line breaks
# and special characters.
# It also solves the problem of csv writer defaulting ',' as "new row" delimiter
def write_row(number, title, description, category):
    encoded_title = base64.b64encode(title.encode())
    encoded_description = base64.b64encode(description.encode())

    string_var = [number, encoded_title, encoded_description, category]
    writer(string_var)


# Helper function for writing to file
my_fields = ['number', 'title', 'description', 'category']  # csv columns  # for DictWriter headers

# Number that stores the current question number being scraped
# instance var
q_number = 0

# Incrementer for keeping track of position in list
incrementer = 0

# # Load incrementer file number from previous session on first run if counter file exists
# If the path exists and file is not empty
if not path.exists("export/numberlist.data") or os.stat("export/numberlist.data").st_size == 0:
    generate_num_range()
    sys.exit("generated list")
else:
    question_list = read_next_question_list()  # instance access for random number list

    # Load previous iteration if it exists
    if path.exists("incrementer.txt") and os.stat("incrementer.txt").st_size != 0:
        m = open("incrementer.txt", "r")
        incrementer = int(m.readline())
        m.close()


# This method writes or appends to the csv file using
# question number: question number from random number list
# title: encoded in base64, first 15 or so characters of description
# description: encoded in base64
# question category ie. 'Physics'
def writer(string_var):
    my_file = open('export/questions.csv', 'a')
    write = csv.DictWriter(my_file, fieldnames=my_fields)

    if q_number <= 1 or os.stat("export/questions.csv").st_size == 0:
        write.writeheader()

    write.writerow({'number': f'{string_var[0]}', 'title': f'{string_var[1]}', 'description': f'{string_var[2]}',
                    'category': f'{string_var[3]}'})


# Perform all functions required to gather the html of a page while avoiding bot detection
# Must be outside 'collect_page()' so that a new instance is not created for each iteration
opts = Options()
opts.add_argument("Mozilla/5.0 (compatible; GoogleDocs; apps-spreadsheets; +http://docs.google.com)")
opts.add_argument("--window-size=1920,1080")
opts.add_extension("extension_1_4_0_0.crx")
chrome_browser = webdriver.Chrome(options=opts, executable_path='chromedriver.exe')


# This method uses selenium to extract the html from the page and preserve the session cookies
def collect_page():
    try:
        # Setting the user agent
        # Sets the user agent for functions in collect_page(), which is called in the primary loop.

        # Disguise the request as google IP range service
        # User-Agent': 'Mozilla/5.0 (compatible; GoogleDocs; apps-spreadsheets; +http://docs.google.com)
        # Run through all questions in archive by using q###### schema
        # https://www.chegg.com/homework-help/questions-and-answers/q
        # url = "http://patspace.me"

        url = 'https://www.chegg.com/homework-help/questions-and-answers/q' + str(q_number)  # Define URL
        chrome_browser.get(url)  # the url
        print(str(x) + " - Scraping: " + url)
        time.sleep(random.uniform(0.5, 1))

        # Faking user interactions
        element_to_hover_over = chrome_browser.find_element_by_xpath("/html/body/div[1]/div[4]/oc-component/div["
                                                                     "1]/div/div[1]/div")
        # ActionChains(chrome_browser).move_to_element(element_to_hover_over).perform()
        # time.sleep(random.uniform(0.5, 1))
        # ActionChains(chrome_browser).click()
        # time.sleep(random.uniform(0.5, 1))
        # -- umatrix testing
        # scroll_down_arrow = chrome_browser.find_element_by_xpath("/html/body/div[1]/div[4]/oc-component/div["
                                                                # "1]/div/nav/ul/li[11]/a/span")
        # TouchActions(chrome_browser).long_press(scroll_down_arrow)

        content = chrome_browser.page_source  # grab html from the page
        return content  # method then returns the html content of the page
    except NoSuchElementException:
        print("Failed to implement anti-detection measures; missing element (or recaptcha present)\n")


# Run through every page in the database and store url to text file
for x in range(incrementer, 4000000):
    # Should reset at the start of each loop
    title_string = ''
    desc_string = ''
    temp_string_array = []  # holds the final output values written to questions.csv
    # current_question = read_increment_to_use()  # find a random question to scrape (no duplicates)
    q_number = question_list[x]  # assign list question_list the increment [1++] to be question number

    try:
        # page = urlopen(req).read()  # take request and read
        soup = BeautifulSoup(collect_page(), 'html.parser')  # parse request to html

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
            write_row(q_number, title_string, desc_string, category)

        else:  # Otherwise move to the next function
            pass
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

atexit.register(save_counter)  # At normal program close, save the text file
