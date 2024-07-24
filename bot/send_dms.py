from multiprocessing import Process
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from bs4 import BeautifulSoup
import time
import random
import re
import os
from . import pick_random_message_for_DM
from .proxy import get_free_proxy


def initialize_processes_for_sending_dm(cookies, message_limit: int, foryou_time: int ) -> None:
    with open('scraped_users.txt', 'r') as users:
        recievers = [user.strip('\n') for user in users.readlines()]
    print("DM Sending Process Started.")
    DM_Sender(cookies, recievers, message_limit, foryou_time)
    return None

# Function to send DMs to given recivers list
def DM_Sender(cookies, recivers: list, message_limit: int, foryou_time: int):
    options = uc.ChromeOptions()
    options.add_argument(f'proxy-server={get_free_proxy()}')
    driver = uc.Chrome(options=options)

    # Add the sessionID cookie and refresh the page
    driver.get(f'https://www.tiktok.com')
    driver.add_cookie({'name': 'sessionid', 'value': cookies})
    driver.refresh()

    msg_round_counter = 0
    for idx, reciver in enumerate(recivers):
        driver.get(f'https://www.tiktok.com/@{reciver}')
        time.sleep(3)

        wait = WebDriverWait(driver, 10)
        try:
            follow_button = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div[1]/div[2]/div/div[1]/button")))
            follow_button.click()
        except:
            _follow_button = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div[1]/div[2]/div/div[2]/a/button")))
            print("Already followed")
        input("enter for follow")
        # Get the page source HTML
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        message_link_elements = soup.find_all('a', href=True)
        message_link = None

        for element in message_link_elements:
            button = element.find('button', type='button')
            if button and 'Messages' in button.text:
                message_link = element['href']
                break

        if message_link:
            match = re.search(r'/messages\?lang=en&u=\d+', message_link)
            if match:
                extracted_link = match.group()
                dm_link = f'https://www.tiktok.com{extracted_link}'
            else:
                print("Got DM Link.")
        else:
            print("Couldn't finf DM Link.")
            input()
            continue

        driver.get(dm_link)

        # get random message from messages.txt
        message = pick_random_message_for_DM()

        # target message box, send button and send message
        message_input = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "public-DraftEditor-content")))
        msg = message.strip("\n")
        message_input.send_keys(f'{msg}')

        send_dm_btn = driver.find_element(By.CLASS_NAME, "css-d7yhdo-StyledSendButton")
        send_dm_btn.click()
        time.sleep(2)

        if (idx > message_limit + msg_round_counter*idx):
            driver.get("https://www.tiktok.com/foryou?lang=en")
            msg_round_counter += 1
            cur_time = time.time()
            while(cur_time > time.time() -  foryou_time):
                driver.execute_script("window.scrollTo(window.scrollY, window.scrollY + 700);")
                time.sleep(random.randint(10, 20))
    
    driver.quit()