from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import time
from datetime import datetime
import random
import os
import io  # for utf-8 encoding bug fix


# Helper function for writing to file
def writer(file, mode, string_var):
    # io.open to fix "'charmap' codec can't encode character
    # '\u03c7' in position 309: character maps to <undefined>"
    # '\u03a9' \u2212 etc.
    f = io.open(f"{file}", f"{mode}", encoding="utf-8")
    f.write(f"{string_var}")
    f.write("\n")
    f.close()


incrementer = 976
# Run through every page in the database and store url to text file
for x in range(incrementer, 4000000):
    # Should reset at the start of each loop
    title_string = ''
    desc_string = ''

    # Run through all questions in archive by using q###### schema
    url = "https://www.chegg.com/homework-help/questions-and-answers/q" + str(incrementer)
    incrementer += 1

    # Disguise the request as google IP range service
    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; GoogleDocs; apps-spreadsheets; +http://docs.google.com)',
        "Accept-Language": "en-US, en;q=0.5"
    })
    print(str(x) + " - Grabbing: " + url)
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

            # Save titles to titles.txt
            if not (os.path.isfile("export/questions.txt")) or os.stat("export/questions.txt").st_size == 0:
                writer('export/questions.txt', 'w', title_string.replace('\n', ' '))  # create questions.txt
                writer('export/questions.txt', 'a', desc_string.replace('\n', ' '))
                writer('export/questions.txt', 'a', "\n\n")  # new line
            else:
                writer('export/questions.txt', 'a', title_string.replace('\n', ' '))
                writer('export/questions.txt', 'a', desc_string.replace('\n', ' '))
                writer('export/questions.txt', 'a', "\n\n")  # new line

        else:  # Otherwise move to the next function
            pass
    except Exception as e:
        print(e)
        # Export error log to file
        m = open("export/error_log.txt", "a")
        m.write(str(e))
        m.write('\n')
        m.write("Iteration interrupted at question: " + str(incrementer))
        m.write('\n')
        m.write("@" + str(datetime.now()))
        m.write('\n')
        m.close()
        x = x - 1
        incrementer = x  # start from last stop
        # Wait between 8 and 10 minutes if blocked
        time.sleep(random.randint(800, 1000))
        pass
