from multiprocessing import Pool
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from concurrent.futures import ThreadPoolExecutor
from typing import List
import time
import subprocess

from . import scroll_to_bottom, login_account
from .proxy import get_free_proxy

def kill_chromedriver():
    try:
        # Command to forcefully kill all instances of chromedriver.exe
        subprocess.run(['taskkill', '/F', '/IM', 'chromedriver.exe'], check=True)
        print("All instances of chromedriver.exe have been successfully closed.")
    except subprocess.CalledProcessError as e:
        # This exception is raised if the taskkill command fails
        print(f"An error occurred while trying to close chromedriver.exe: {e}")
    
def initialize_processes_for_scraping(usernames: List[str], cookies) -> None:
    # cookies = login_account()
    # using threads
    # with ThreadPoolExecutor(max_workers=3) as executor:
    #     futures = [executor.submit(scrape_followers, username, cookies) for username in usernames]
    #     for future in futures:
    #         future.result()
    # simple calls
    for username in usernames:
        scrape_followers(username, cookies)

# Function to scrape followers using sessionID cookie
def scrape_followers(username: str, cookies) -> None:
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument(r'--no-sandbox')
    # chrome_options.add_argument(f'--proxy-server={get_free_proxy()}')
    driver = uc.Chrome(options=chrome_options)
    driver.get('https://www.tiktok.com')
    driver.add_cookie({'name': 'sessionid', 'value': cookies})
    driver.refresh()
    print(f"Starting followers scraping for @{username} .....")

    # Add the sessionID cookie and refresh the page
    driver.get(f'https://www.tiktok.com/@{username}')
    time.sleep(2)

    # guest_button = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div[3]/div/div/div/div[1]/div/div/div[3]/div/div[2]/div/div/div')))
    # guest_button.click()

    # Locating the followers element
    try:
        followers_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="css-mgke3u-DivNumber e1457k4r1"]/strong[@title="Followers" and @data-e2e="followers-count"]')))
    except TimeoutException:
        print("Time out")
        driver.quit()
        return

    followers_count = followers_element.text
    print(f"Number of followers for @{username}: {followers_count}\n")
    
    # input("press enter after ....")
    followers_element.click()

    try:
        # Waiting for the followers modal to be visible
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".css-wq5jjc-DivUserListContainer")))
    except TimeoutException:
        print("Time out")
        driver.quit()
        return

    # Scrolling to the bottom of the followers list
    print(f"Loading followers list for @{username} .....\n")
    scroll_to_bottom(driver)

    # Extracting the followers' information
    print(f"Extracting followers' information for @{username}.....\n")
    followers_list = driver.find_elements(By.CSS_SELECTOR, "li .css-1q2pvy0-DivUserItem a")
    followers = [follower.get_attribute('href').split('/')[-1][1:] for follower in followers_list]
    driver.quit()

    # Store followers in a text file
    print(f"Storing followers of @{username} in a text file .....\n")
    with open(f'follower_scraps/{username}_followers.txt', 'w') as file:
        for follower in followers:
            file.write(f"{follower}\n")

    print(f"Followers for @{username} have been stored in '{username}_followers.txt'\n")
    driver.quit()
    time.sleep(3)
    return

# Function to scrape usernames from comment section of given POST_URL
def scrape_commenters(post_url: str, cookies, output_file: str):
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)

    # Add the sessionID cookie and refresh the page
    driver.get(f'https://www.tiktok.com')
    driver.add_cookie({'name': 'sessionid', 'value': cookies})
    driver.refresh()
    print("Getting Post URL .....\n")
    driver.get(post_url)

    time.sleep(2)

    wait = WebDriverWait(driver, 10)

    # Wait for the comments section to load
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.css-13revos-DivCommentListContainer')))

    # variables to track the number of comments
    previous_comment_count = 0
    current_comment_count = -1

    # main_comments_container = driver.find_element(By.CSS_SELECTOR, '.css-13revos-DivCommentListContainer')
    print("Loading comments .....\n")
    while previous_comment_count != current_comment_count:
        previous_comment_count = current_comment_count
        # Scroll the body to load new comments
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            # Wait for the new comments to be loaded and visible
            wait.until(
                lambda d: d.find_element
                (By.CSS_SELECTOR, '.css-13revos-DivCommentListContainer')
                .get_attribute('childElementCount') != previous_comment_count
            )

        except TimeoutException:
            # If no new comments are loaded within the timeout period, break the loop
            print("No new comments loaded within the timeout period.")
            break

        except StaleElementReferenceException:
            # If a stale element reference is encountered, find the element again
            continue

        # Get the current number of comments
        comments_container = driver.find_element(By.CSS_SELECTOR, '.css-13revos-DivCommentListContainer')
        current_comment_count = comments_container.get_attribute('childElementCount')

        print(f"Loaded {current_comment_count} comments.")

        # Check if the end of the comments section is reached
        if previous_comment_count == current_comment_count:
            print("Reached the end of the comments section.")
            break

    # Find all comment containers
    comment_containers = driver.find_elements(By.CSS_SELECTOR, "div.css-1mf23fd-DivContentContainer")

    # Write the usernames to the output file, excluding admin replies
    print(f"Writing usernames to '{output_file}' .....\n")
    with open(output_file, 'w', encoding='utf-8') as file:
        for container in comment_containers:
            # Check if the container has a 'Creator' label
            creator_label = container.find_elements(By.CSS_SELECTOR, "span.css-6eutxn-SpanIdentity")
            if not creator_label:  # If there is no 'Creator' label, it's a commenter
                # Find the anchor tag and extract the username from the href attribute
                username_anchor = container.find_element(By.CSS_SELECTOR, "a.css-fx1avz-StyledLink-StyledUserLinkName")
                username = username_anchor.get_attribute('href').split('/')[-1][1:]
                file.write(username + "\n")
    driver.quit() 