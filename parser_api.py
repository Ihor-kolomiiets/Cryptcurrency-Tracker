import sqlite3
import time
import requests
import config


def update(interval=600):  # update db every 10 min
    while True:
        listing_url = 'https://api.coinmarketcap.com/v2/listings/'
        response = requests.get(listing_url)
        coins = response.json()['data']
        conn = sqlite3.connect(config.database)
        cursor = conn.cursor()
        for coin in coins:
            coin_id = coin['id']
            coin_name = coin['name']
            coin_symbol = coin['symbol']
            print(coin_id, coin_name, coin_symbol)
            cursor.execute('INSERT OR IGNORE INTO crypto_json (id, name, symbol) VALUES ("%s", "%s", "%s")'
                           % (coin_id, coin_name, coin_symbol))
        conn.commit()
        cursor.close()
        conn.close()
        prices = {}
        start = 1
        limit = 29  # limit for prevent block
        while True:  # Pars all ticker. Because api has 100 items limit, we should add 100 for next query
            ticker_url = 'https://api.coinmarketcap.com/v2/ticker/?start=%s' % str(start)
            response = requests.get(ticker_url)
            prices_get = response.json()['data']
            prices.update(prices_get)
            start += 100
            print(limit)
            print(prices_get)
            print(start)
            print(ticker_url)
            if limit <= 0:
                break
            else:
                limit -= 1
            if len(prices_get) < 100:  # If dict length less than 100, well than we reach end, and break the loop
                break
        conn = sqlite3.connect(config.database)
        cursor = conn.cursor()
        for price in prices:
            coin_id = prices[price]['id']
            coin_name = prices[price]['name']
            coin_price = prices[price]['quotes']['USD']['price']
            percent_change_1h = prices[price]['quotes']['USD']['percent_change_1h']
            percent_change_24h = prices[price]['quotes']['USD']['percent_change_24h']
            percent_change_7d = prices[price]['quotes']['USD']['percent_change_7d']
            print(coin_id, coin_name, coin_price, percent_change_1h, percent_change_24h, percent_change_7d)
            cursor.execute('UPDATE crypto_json SET price="%s", percent_change_1h="%s", percent_change_24h="%s", '
                           'percent_change_7d="%s" WHERE id="%s" AND name="%s"'
                           % (coin_price, percent_change_1h, percent_change_24h, percent_change_7d, coin_id, coin_name))
        conn.commit()
        print(conn.total_changes)
        cursor.close()
        conn.close()
        time.sleep(interval)


if __name__ == '__main__':
    update()
