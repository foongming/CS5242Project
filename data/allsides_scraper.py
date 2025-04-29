from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os
import time
from random import randrange
import pandas as pd
import datetime as dt
import sys
import logging

logging.basicConfig(filename='allsides_scraper.log', level=logging.ERROR)

def connect_with_selenium(url):
    driver = webdriver.Chrome()
    driver.get(url)
    return driver

def get_allsides_news(driver, hist):
    d = []
    i = 100
    time.sleep(randrange(2, 5))
    news_trio = driver.find_element(By.CSS_SELECTOR, 'div.news-trio')
    while i >= 0:
        news_items = news_trio.find_elements(By.CSS_SELECTOR, 'div.news-item')
        i = min(i, len(news_items)-1)
        news = news_items[i]
        try:
            button = news.find_element(By.TAG_NAME, 'a')
            href = button.get_attribute('href')
            if hist[href]:
                i -= 1
                continue
            else:
                hist[href] = 1
        except NoSuchElementException as e:
            i -= 1
            continue
        orginal_tab = driver.current_window_handle
        driver.switch_to.new_window('tab')
        try:
            driver.get(href)
            time.sleep(randrange(2, 5))
            title = driver.find_element(By.TAG_NAME, 'h1').text
            allsides_summary_text = driver.find_element(By.CSS_SELECTOR, 'div.field-content').text
            external_link = driver.find_element(By.CSS_SELECTOR, 'div.read-more-story').find_element(By.TAG_NAME, 'a').get_attribute('href')
            bias = driver.find_element(By.CSS_SELECTOR, 'div.article-media-bias-').find_element(By.TAG_NAME, 'a').text
            d.append(dict(title=title, allsides_summary_text=allsides_summary_text, external_link=external_link, bias=bias))
        except Exception as e:
            print(e)
            logging.error(e)
        driver.close()
        driver.switch_to.window(orginal_tab)
        i -= 1
    return d, hist

if __name__ == '__main__':
    url = 'https://www.allsides.com/unbiased-balanced-news'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }
    driver = connect_with_selenium(url)
    try:

        if not os.path.exists('data'):
            os.mkdir('data')

        if os.path.exists('data/scraped_urls.txt'):
            with open('data/scraped_urls.txt', 'r') as f:
                hist = f.read().splitlines()
        else:
            hist = []
        hist = defaultdict(lambda: 0, dict(zip(hist, [1]*len(hist))))
        d, hist = get_allsides_news(driver, hist)
        df = pd.DataFrame(d)
        df.to_csv(f'data/allsides_news_{dt.datetime.now().strftime('%Y%d%m%H%M%S')}.csv')
        with open('data/scraped_urls.txt', 'w') as f:
            f.write('\n'.join(hist.keys()))

        driver.close()
    except Exception as e:
        print(e)
        logging.error(e)
        driver.close()
        sys.exit(1)