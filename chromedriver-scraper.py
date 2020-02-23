from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.touch_actions import TouchActions
from selenium.webdriver.chrome.options import Options
import pickle  # Saving the cookies

# Setting the user agent
opts = Options()
opts.add_argument("Mozilla/5.0 (compatible; GoogleDocs; apps-spreadsheets; +http://docs.google.com)")
opts.add_argument("--window-size=1920,1080")

URL = 'https://www.chegg.com/homework-help/questions-and-answers/q'  # Define URL
chromeBrowser = webdriver.Chrome(options=opts, executable_path='chromedriver.exe')

for x in range(8, 9):
    chromeBrowser.get(URL + str(x))
    time.sleep(random.uniform(1, 2))

    # Faking user interactions
    element_to_hover_over = chromeBrowser.find_element_by_id("anyID")
    ActionChains(chromeBrowser).move_to_element(element_to_hover_over).perform()
    time.sleep(random.uniform(0.5, 1.5))
    scroll_up_arrow = chromeBrowser.find_element_by_id("scroll_up")
    TouchActions(chromeBrowser).long_press(scroll_up_arrow)

    # Find the title section
    title = chromeBrowser.find_element(By.XPATH, '/html/body/div[1]/div[5]/div[2]/div['
                                                 '2]/div/oc-component/div/main/div/header/h1')

    print(title)
