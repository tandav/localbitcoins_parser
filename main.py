'''
TODO:
save all, plot only last 48 hours
maybe use only banks in rubles (check different options)
maybe save to parquet/pickle/orc /etc /feather
todo: fix timezone
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
import matplotlib



N_PRICES = 50
DB_PATH  = Path('prices.pkl')
API_URL  = 'https://localbitcoins.net/ru/buy-bitcoins-online/rub'


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
    db = pd.read_csv(DB_PATH, index_col='datetime')
    db.index = pd.to_datetime(db.index)
    now = datetime.datetime.now()
    print(now)
    db.loc[now] = get_prices()
    db.to_csv(DB_PATH, index_label='datetime')

    mean = db.mean(axis=1)

    ax = db.plot(figsize=(16, 10), legend=False, marker=',', linestyle='-', linewidth=0.9)
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    mean.plot(color='black', marker=',', linestyle='-', linewidth=2)
    plt.grid(lw=0.3)
    plt.title(f'updates every minute, last update: {now:%Y %b %d %H:%M:%S} \n')
    plt.ylabel('1 BTC price in RUB')
    plt.xlabel(f'{API_URL}   (top 50 offers, sorted)')
    plt.tight_layout()
    ax.figure.savefig('prices.png')
    fig = ax.get_figure()
    plt.close(fig)

    time.sleep(55)



