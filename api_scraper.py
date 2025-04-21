
from datetime import datetime as dt
import os
import requests
import logging
import json
from constants import RAPID_API_KEY
from constants import NEWSDATA_API_KEY, WORLDNEWS_API_KEY
import pandas as pd
import os
import logging

import worldnewsapi
from worldnewsapi.rest import ApiException


newsapi_configuration = worldnewsapi.Configuration(api_key={'apiKey': WORLDNEWS_API_KEY})
newsapi_instance = worldnewsapi.NewsApi(worldnewsapi.ApiClient(newsapi_configuration))

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
    return mbfc_data


def get_mbfc_ratings(mbfc_data_from_file):
    if mbfc_data_from_file:
        mbfc_file = sorted(list(filter(lambda x: x.startswith('mbfc'), os.listdir("data/"))))
        
        with open(os.path.join('data', mbfc_file[-1]), 'r') as f:
            mbfc = json.load(f)
    else:
        mbfc = get_mbfc_data()
    return pd.DataFrame(mbfc)

def get_news_sources(newsapi_data_from_file):
    if newsapi_data_from_file:
        sources_file = sorted(list(filter(lambda x: x.startswith('newsdata_sources'), os.listdir("data/"))))

        with open(os.path.join('data', sources_file[-1]), 'r') as f:
            sources = json.load(f)
            df = pd.DataFrame(sources['results'])

    else:
 
        top_url=f"https://newsdata.io/api/1/sources?apikey={NEWSDATA_API_KEY}&category=politics&language=en&prioritydomain=top"
        gen_url=f"https://newsdata.io/api/1/sources?apikey={NEWSDATA_API_KEY}&category=politics&language=en&"
        us_url=f"https://newsdata.io/api/1/sources?apikey={NEWSDATA_API_KEY}&country=us&category=politics&language=en&prioritydomain=top"
        uk_url=f"https://newsdata.io/api/1/sources?apikey={NEWSDATA_API_KEY}&country=gb&category=politics&language=en&prioritydomain=top"
        ca_url=f"https://newsdata.io/api/1/sources?apikey={NEWSDATA_API_KEY}&country=ca&category=politics&language=en&prioritydomain=top"

        dfs = []

        for url in [top_url, gen_url, us_url, uk_url, ca_url]:
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()
                with open(f"data/newsdata_sources_{dt.now().strftime('%Y%m%d%H%M%S')}.json", "w") as f:
                    json.dump(data, f)
                dfs.append(pd.DataFrame(data['results']))

        df = pd.concat(dfs)
    df['cleaned_url'] = df.url.str[8:].str.replace('www.', '')

    return df

def get_ratings_master(mbfc_data_from_file=True, newsapi_data_from_file=True):

    mbfc_df = get_mbfc_ratings(mbfc_data_from_file) 
    mbfc_df = mbfc_df[mbfc_df.Bias.isin(['Left', 'Right', 'Left-Center', 'Right-Center', 'Least Biased'])]

    sources_df = get_news_sources(newsapi_data_from_file)

    ratings_master = sources_df.merge(mbfc_df, left_on='cleaned_url', right_on='Source URL', how='inner')
    ratings_master.to_csv('data/ratings_master.csv', index=False)

    return ratings_master

def get_news(ratings_master):
    biases = ['Left-Center', 'Right-Center', 'Left', 'Least Biased', 'Right']
    dfs = []
    while True:
        for bias in biases:
               
            if not os.path.exists(f"data/sources_{bias}.txt"):
                with open(f"data/sources_{bias}.txt", "w") as f:
                    f.write(','.join(ratings_master[ratings_master.Bias == bias].cleaned_url.tolist()))
            with open(f"data/sources_{bias}.txt", "r") as f:
                sources = f.read()
                sources = sources.split(',')
                    
            try:            
                res = newsapi_instance.search_news(
                            text='',
                            language='en',
                            news_sources=','.join(sources)
                ) 
            except ApiException as e:
                # keep going until the API limit is reached
                if e.status == 402:
                    logging.error(f"API limit reached: {e}")
                    if dfs:
                        df = pd.concat(dfs)
                        df.to_csv(f'data/newsapi_data_{dt.now().strftime('%Y%m%d%H%M%S')}.csv', index=False)
                    else:
                        df = pd.DataFrame()
                    return df
                else:
                    logging.error(f"API error: {e}")
                    df = pd.concat(dfs)
                    df.to_csv(f'data/newsapi_data_{dt.now().strftime('%Y%m%d%H%M%S')}.csv', index=False)
                    return df
               
            if res.news:
                d = []
                for n in res.news:
                    d.append(n.to_dict())
                res_df = pd.DataFrame(d)
                dfs.append(res_df)
            else:
                print(f"no news articles found for {bias}")
                continue

            collected_urls = res_df.url.str.split('/').str[2].str.split('www.').str[1].unique().tolist()
            for url in collected_urls:
                # this is probably slow but the list is expected to be short
                if url in sources:
                    sources.remove(url)
            # archive old sources file, and create a new one
            os.rename(f"data/sources_{bias}.txt", f"data/sources_{bias}_{dt.now().strftime('%Y%m%d%H%M%S')}.txt")
            with open(f"data/sources_{bias}.txt", "w") as f:
                f.write(','.join(sources))

if __name__ == '__main__':
    ratings_master = get_ratings_master(newsapi_data_from_file=True, mbfc_data_from_file=True) # change these to false to call new data from API
    news_df = get_news(ratings_master)