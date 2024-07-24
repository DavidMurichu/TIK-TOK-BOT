import os
from typing import List

from bot import getUsernames, login_account
from bot.scraping import initialize_processes_for_scraping, scrape_commenters
from bot.send_dms import initialize_processes_for_sending_dm


def menu() -> None:
    print("*" * 40)
    print("TikTok Scraper & Mass DM Sender Tool")
    print("*" * 40)
    print()
    print("Choose an option:")
    print("1. Scrape followers from a list of usernames")
    print("2. Scrape followers from a Post's Comment Section")
    print("3. Send DMs to scraped followers")
    print("4. Exit")


def main():
    print("Cookies")
    print("1. get from file")
    print("2. get from login")
    choice = int(input("Enter your choice: (1 - 2): "))
    if choice == 1:
        with open('cookies.txt', 'r') as file:
            cookies = file.read()
    else:
        cookies = login_account()
        with open('cookies.txt', 'w') as file:
            file.write(cookies)
    while 1:
        menu()
        choice = int(input("\nEnter your choice: (1 - 3): "))
        if choice == 1:
            usernames: List[str] = getUsernames()
            initialize_processes_for_scraping(usernames, cookies)
        elif choice == 2:
            post_url: str = input("Enter the post url: ")
            scrape_commenters(post_url, cookies, 'commentor_usernames.txt')
        elif choice == 3:
            message_limit = 20
            foryou_time = 1*60
            initialize_processes_for_sending_dm(cookies, message_limit, foryou_time)
        elif choice == 4:
            print("Exiting...")
            break        
        else:
            print("Invalid choice")

if __name__ == '__main__':
    main()
