import pandas as pd
import os

if __name__ == "__main__":
    data_files = os.listdir('data')
    allsides_files = [f for f in data_files if f.startswith('allsides_news')]
    api_files = [f for f in data_files if f.startswith('newsapi_data')]

    allsides_l = []
    for f in allsides_files:
        allsides_l.append(pd.read_csv(f'data/{f}'))

    api_l = []
    for f in api_files:
        api_l.append(pd.read_csv(f'data/{f}'))


    all_sides_data = pd.concat(allsides_l)
    api_data = pd.concat(api_l)

    all_sides_data = all_sides_data.drop_duplicates()
    api_data = api_data.drop_duplicates()

    print('data from all sides exported:', f'{len(all_sides_data)} rows')
    print('data from api exported:', f'{len(api_data)} rows')

    all_sides_data.to_csv('allsides_news_data.csv', index=False)
    api_data.to_csv('newsapi_data.csv', index=False)
