from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import sys
import time
import random
import csv

# Run through every page in the database and store url to text file
for x in range(3, 4):
    url = "https://www.chegg.com/homework-help/questions-and-answers/q" + str(x)

    # Disguise the request as standard browser (firefox)
    req = Request(url,
                  headers={'User-Agent': 'APIs-Google (+https://developers.google.com/webmasters/APIs-Google.html)'})
    print("Grabbing: " + url)
    time.sleep(random.randint(1, 3))  # Avoid automation suspicion

    try:
        page = urlopen(req).read()  # take request and read
        soup = BeautifulSoup(page, 'html.parser')  # parse request to html

        # Detect if captcha is on the page
        is_captcha_on_page = soup.find("input", id="recaptcha-token") is not None
        if is_captcha_on_page:
            sys.exit()

        # Find the question title
        title_array = np.array
        for EachPart in soup.select('h1[class*="PageHeading-"]'):
            # print(EachPart.get_text() + "\n")
            title = EachPart.get_text
            title_array = np.array([title])  # Save to numpy array col1

        # Find the full question text
        desc_array = np.array
        for EachPart in soup.select('section[class*="QuestionBody__QuestionBodyWrapper-sc-"]'):
            # print(EachPart.get_text())
            desc = EachPart.get_text
            
            desc_array = np.array([EachPart.get_text])  # Save to numpy array col2

        # Transpose data into two columns
        data = np.array([title_array, desc_array])
        data = data.T

        # Open ASCII file
        datafile_path = "questions.csv"
        with open(datafile_path, 'w+') as datafile_id:
            np.savetxt(datafile_id, data, fmt=['%s', '%s'])  # Write to the file
    except Exception as e:
        print(e)
        sys.exit()
