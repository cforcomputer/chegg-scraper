from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import sys
import time
import random

# Run through every page in the database and store url to text file

title_string = ''
desc_string = ''

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
        for EachPart in soup.select('h1[class*="PageHeading-"]'):
            # print(EachPart.get_text() + "\n")
            title_string += EachPart.get_text(strip=True)

        # Find the full question text
        for EachPart in soup.select('section[class*="QuestionBody__QuestionBodyWrapper-sc-"]'):
            # print(EachPart.get_text())
            desc_string += EachPart.get_text(strip=True)

    except Exception as e:
        print(e)
        sys.exit()

with open('titles.csv', 'w', newline='') as csv_file:
    csv_file.write(title_string)

with open('descriptions.csv', 'w', newline='') as csv_file:
    csv_file.write(desc_string)
