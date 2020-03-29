'''
TODO:
save all, plot only last 48 hours
maybe use only banks in rubles (check different options)
fix stddev
track each user
maybe plot only +- 3std (drop outliers)
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
DB_PATH  = Path('db.pkl')
API_URL  = 'https://localbitcoins.net/ru/buy-bitcoins-online/rub'
MSK = dateutil.tz.gettz('Europe/Moscow')
DATE_FORMAT = DateFormatter('%H:%M', tz=MSK)
PRICE_FORMAT = StrMethodFormatter('{x:,.0f}')
YLIM = 20 # stddev


if len(sys.argv) == 2 and sys.argv[1] == 'init':
    assert not DB_PATH.exists()
    pd.DataFrame().to_pickle(DB_PATH)
    print('init done')
    sys.exit(0)


def get_ads():
    _ = API_URL
    _ = requests.get(_)
    _ = _.text
    _ = BeautifulSoup(_, features='html.parser')
    _ = _.find_all('tr', class_='clickable')
    return _


while True:
    d = pd.read_pickle(DB_PATH)
    now = datetime.datetime.now(tz=MSK)

    for row in get_ads():
        # user  = row.find('td', class_='column-user').find('a').attrs['href'].split('/')[-2]
        ad    = row.find('td', class_='column-button').find('a').attrs['href'].split('/')[2]
        price = float(row.find('td', class_='column-price').text.strip()[:-4].replace(',', ''))
        d.loc[now, ad] = price
    print(now, d.shape)
    d.to_pickle(DB_PATH)

    mean = d.mean(axis=1)
    std  = d.std(axis=1)

    mean_global = d.mean().mean()
    std_global = d.std().mean()

    ax = d.interpolate(limit_area='inside').plot(figsize=(16, 10), legend=False, marker=None, linestyle='-', linewidth=0.9)
    ax.xaxis.set_major_formatter(DATE_FORMAT)
    ax.yaxis.set_major_formatter(PRICE_FORMAT)
    mean.plot(color='black', marker=',', linestyle='-', linewidth=3)
    plt.fill_between(std.index, mean - std, mean + std, color='grey', alpha=.1, zorder=-1)
    plt.ylim(mean_global - YLIM * std_global, mean_global + YLIM * std_global)
    plt.grid(lw=0.3)
    plt.title(f'{API_URL}   | top 50 offers from 1st page')
    plt.xlabel(f'updates every minute, last update: {now:%Y %b %d %H:%M:%S} MSK')
    plt.ylabel('1 BTC price in RUB')
    plt.tight_layout()
    ax.figure.savefig('prices2.png')
    fig = ax.get_figure()
    plt.close(fig)

    # time.sleep(55)
    time.sleep(5)



