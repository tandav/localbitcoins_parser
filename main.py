'''
TODO:
save all, plot only last 48 hours
maybe use only banks in rubles (check different options)
fixstddev
'''


from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
from pathlib import Path
import sys
import time
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
from matplotlib.dates import DateFormatter
import matplotlib
import dateutil



N_PRICES = 50
DB_PATH  = Path('prices.pkl')
API_URL  = 'https://localbitcoins.net/ru/buy-bitcoins-online/rub'
MSK = dateutil.tz.gettz('Europe/Moscow')
DATE_FORMAT = DateFormatter('%H:%M', tz=MSK)
PRICE_FORMAT = StrMethodFormatter('{x:,.0f}')

if len(sys.argv) == 2 and sys.argv[1] == 'init':
    assert not DB_PATH.exists()
    d = pd.DataFrame(data=[], columns=range(N_PRICES))
    d.index = pd.to_datetime(d.index)
    d.to_pickle(DB_PATH)
    print('init done')
    sys.exit(0)


def get_prices():
    _ = API_URL
    _ = requests.get(_)
    _ = _.text
    _ = BeautifulSoup(_, features='html.parser')
    _ = _.find_all('td', class_='column-price')
    _ = map(lambda x: x.text            , _)
    _ = map(lambda x: x.strip()         , _)
    _ = map(lambda x: x.replace(',', ''), _)
    _ = map(lambda x: x[:-4]            , _)
    _ = map(float                       , _)
    _ = sorted(_)
    assert len(_) == N_PRICES
    return _


while True:
    db = pd.read_pickle(DB_PATH)
    now = datetime.datetime.now(tz=MSK)
    print(now)
    db.loc[now] = get_prices()
    db.to_pickle(DB_PATH)

    mean = db.mean(axis=1)

    ax = db.plot(figsize=(16, 10), legend=False, marker=',', linestyle='-', linewidth=0.9)
    ax.xaxis.set_major_formatter(DATE_FORMAT)
    ax.yaxis.set_major_formatter(PRICE_FORMAT)
    mean.plot(color='black', marker=',', linestyle='-', linewidth=3)
    plt.grid(lw=0.3)
    plt.title(f'{API_URL}   (top 50 offers, sorted)')
    plt.xlabel(f'updates every minute, last update: {now:%Y %b %d %H:%M:%S} MSK')
    plt.ylabel('1 BTC price in RUB')
    plt.tight_layout()
    ax.figure.savefig('prices.png')
    fig = ax.get_figure()
    plt.close(fig)

    time.sleep(55)



