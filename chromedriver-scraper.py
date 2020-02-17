from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime
import time
import argparse
import os
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.touch_actions import TouchActions
from selenium.webdriver.common.keys import Keys   # For keyboard keys

URL = 'https://www.chegg.com/homework-help/questions-and-answers/q'      # Define URL
chromeBrowser = webdriver.Chrome(executable_path='chromedriver.exe')

for x in range(8, 9):
    chromeBrowser.get(URL + str(x))
    time.sleep(random.randrange(2.5, 3.5))

    # Faking user interactions
    element_to_hover_over = chromeBrowser.find_element_by_id("anyID")
    ActionChains(chromeBrowser).move_to_element(element_to_hover_over).perform()
    scroll_up_arrow = chromeBrowser.find_element_by_id("scroll_up")
    TouchActions(chromeBrowser).long_press(scroll_up_arrow)

    # Find the title section
    title = chromeBrowser.find_element(By.XPATH, '/html/body/div[1]/div[5]/div[2]/div['
                                                 '2]/div/oc-component/div/main/div/header/h1')
