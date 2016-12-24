#!../venv/bin/python
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def init_driver():
    driver = webdriver.Firefox()
    driver.wait = WebDriverWait(driver, 5)
    return driver


def lookup(driver, query):
    driver.get("http://www.hearthpwn.com/decks?filter-build=31")
    time.sleep(1)
    driver.get("http://www.hearthpwn.com/decks?filter-build=31&filter-class=1024&filter-deck-tag=1&filter-player=126&filter-show-standard=1&sort=-viewcount")
    time.sleep(2)
    html_source = driver.page_source
    from hearthpwn.hearthpwn_scraper import parse_decks_listing
    res = parse_decks_listing(html_source)
    print res


driver = init_driver()
lookup(driver, "Selenium")
time.sleep(2)
driver.quit()
