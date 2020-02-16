from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import sys
import time
import random
import os
from selenium import webdriver
from fake_useragent import UserAgent

title_string = ''
desc_string = ''
bread_string = ''


# This function generates a random user agent
def get_random_ua():
    ua = UserAgent()
    ua.update()  # Update useragent database
    return ua.random


# Helper function for writing to file
def writer(file, mode, string_var):
    f = open(f"{file}", f"{mode}")
    f.write(f"{string_var}")
    f.write('\n')
    f.close()


# Run through every page in the database and store url to text file
for x in range(10, 13):

    # Run through all questions in archive by using q###### schema
    url = "https://www.chegg.com/homework-help/questions-and-answers/q" + str(x)

    # Web driver testing

    # Disguise the request as standard browser (firefox) + trusted bot/service
    req = Request(url, headers={
        'User-Agent': get_random_ua()
    })
    print("Grabbing: " + url)
    # Reduce suspicion by grabbing page at random intervals
    time.sleep(random.randint(1, 3))

    try:
        page = urlopen(req).read()  # take request and read
        soup = BeautifulSoup(page, 'html.parser')  # parse request to html

        # Find the question title
        if soup.select('h1[class*="PageHeading-"]'):  # if the page is a q&a page

            # Find the category of the question
            for EachCategory in soup.findAll('a[class*="BreadcrumbLink-sc-"]'):
                bread_string = EachCategory.get_text(strip=True)
                # print(EachPart.get_text())
                # Concat. each separate string to fill one row

            for EachTitle in soup.select('h1[class*="PageHeading-"]'):
                # print(EachPart.get_text() + "\n")
                # Concat. each separate string to fill one row
                title_string = EachTitle.get_text(strip=True)

            # Find the full question text
            for EachDescription in soup.select('section[class*="QuestionBody__QuestionBodyWrapper-sc-"]'):
                # print(EachPart.get_text())
                # Concat. each separate string to fill one row
                desc_string = EachDescription.get_text(strip=True)

            # Save titles to titles.txt
            if not (os.path.isfile("titles.txt")) or os.stat("titles.txt").st_size == 0:
                writer('titles.txt', 'w', title_string.replace('\n', ''))
            else:
                writer('titles.txt', 'a', title_string.replace('\n', ''))

            # Save descriptions to descriptions.txt
            if not os.path.isfile("description.txt") or os.stat("description.txt").st_size == 0:
                writer('description.txt', 'w', desc_string.replace('\n', ''))
            else:
                writer('description.txt', 'a', desc_string.replace('\n', ''))

            # Save associated categories to breadcrumbs.txt
            if not os.path.isfile("breadcrumb.txt") or os.stat("breadcrumb.txt").st_size == 0:
                writer('breadcrumb.txt', 'w', (bread_string + ' / ').replace('\n', ''))
            else:
                writer('breadcrumb.txt', 'a', (bread_string + ' / ').replace('\n', ''))

    except Exception as e:
        print(e)
        m = open("error_log", "w")
        m.write(str(e))
        m.write("\n Iteration interrupted at question: " + str(x))
        m.close()
        sys.exit()
