
from datetime import datetime as dt
import os
import requests
import logging
import json
from constants import RAPID_API_KEY

logging.basicConfig(filename='api_scraper.log', level=logging.ERROR)

def get_mbfc_data():
    url = "https://media-bias-fact-check-ratings-api2.p.rapidapi.com/fetch-data"
    headers = {
        "x-rapidapi-host": "media-bias-fact-check-ratings-api2.p.rapidapi.com",
        "x-rapidapi-key": RAPID_API_KEY
    }
    d = requests.get(url, headers=headers)

    try:
        mbfc_data = json.loads(d.text[1:])
        if not os.path.exists("data"):
            os.mkdir("data")

        with open(f"data/mbfc_data_{dt.now().strftime('%Y%d%m%H%M%S')}.json", 'w') as f:
            json.dump(mbfc_data, f)
    except Exception as error:
        logging.ERROR(error)


def get_news_data():
    pass



if __name__ == '__main__':
    get_mbfc_data()