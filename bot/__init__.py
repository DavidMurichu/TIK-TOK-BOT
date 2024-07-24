import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from bs4 import BeautifulSoup
import time, os, random, shutil, multiprocessing, re
from typing import List, Optional

from .proxy import get_free_proxy


def login_account() -> Optional[str]:
    user_email, password = get_account_creds_for_scraping()
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument(r'--no-sandbox')
    # chrome_options.add_argument(f'--proxy-server={get_free_proxy()}')
    driver = uc.Chrome(options=chrome_options)
    driver.get('https://www.tiktok.com')

    try:
        # Finding the top header login button and clicking on it
        header_login_btn = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div/div[3]/button')))
        header_login_btn.click()
    except ElementClickInterceptedException:
        pass
    # clicking on 'Use phone / email / username' button  and choosing 'login with email or username'
    time.sleep(2)
    use_email_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div[3]/div/div/div[1]/div[1]/div/div/div/div[2]/div[2]/div[2]/div/div')))
    # use_email_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//p[text()="Use phone / email / username"]')))
    use_email_btn.click()

    login_with_email_l = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[text()="Log in with email or username"]')))
    login_with_email_l.click()

    time.sleep(2)
    # Finding the login button & input elements for email and password and send 'email' and 'pass' keys
    email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[3]/div/div/div/div[1]/div/form/div[1]/input')))
    email_input.send_keys(f"{user_email}")

    password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[3]/div/div/div/div[1]/div/form/div[2]/div/input')))
    password_input.send_keys(f"{password}")

    main_login_btn = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div[3]/div/div/div/div[1]/div/form/button')))
    main_login_btn.click()

    # Waiting for the captcha to be solved
    input("Press Enter after solving captcha")
    time.sleep(7)
    all_cookies = driver.get_cookies()
    sessionid_value = next((item['value'] for item in all_cookies if item['name'] == 'sessionid'), None)
    driver.quit()
    return sessionid_value


# Function to scroll to the bottom of the followers list
def scroll_to_bottom(driver: uc.Chrome) -> None:
    last_height = driver.execute_script("return document.querySelector('.css-wq5jjc-DivUserListContainer').scrollHeight")
    while True:
        driver.execute_script("document.querySelector('.css-wq5jjc-DivUserListContainer').scrollTo(0, document.querySelector('.css-wq5jjc-DivUserListContainer').scrollHeight);")
        time.sleep(0.5)  # Wait to load page
        new_height = driver.execute_script("return document.querySelector('.css-wq5jjc-DivUserListContainer').scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Function to get usernames for which we wanna sracpe followers from their followers list
def getUsernames() -> List[str]:
    usernames = []
    with open('usernames.txt', 'r') as file:
        for username in file:
            usernames.append(username.strip())
    return usernames

# Function to get account credentials of the account used for Scraping
def get_account_creds_for_scraping():
    with open('account_creds_for_scraping.txt', 'r') as f:
        creds = f.read().split(':')
        return creds[0], creds[1]


# Function to pick random message from messages.txt file for DM Sending
def pick_random_message_for_DM():
    with open('DM_messages.txt', 'r', encoding='utf-8') as f:
        messages = f.readlines()
        return random.choice(messages)
    








