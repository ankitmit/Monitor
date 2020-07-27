import utils
import requests
import json
import stock
import yfinance as yf

_BASE_URL = 'https://finnhub.io/api/v1/quote?symbol='
#BASE_URL = 'https://api.iextrading.com/1.0/stock/market/batch?types=quote&symbols='

def _GetCurrentPrice(ticker, logger):
    url= _BASE_URL + ticker
    logger.info(url)
    print url
    json_obj_list = {}
    try:
        myResponse = requests.get(url)
        print(myResponse)
        if myResponse.ok:
            print('here')
            price = float(myResponse.json()['c'])
            print price
            return price
        else:
            raise Exception('Response not OK to get price of the ticker.')

    except:
        logger.info("Shit broke while getting prices.")
        raise Exception("Cannot get prices.")
    return json_obj_list

class AllStocks:
    def __init__(self, logger):
        self.tickers = ''
        self.stocks_instances = []
        self.logger = logger

    def populateAllStocks(self, data):
        self.tickers = ''
        self.stocks_instances = []
        allRows = data.split('\n')
        tickers_list = []
        for line in allRows:
            row = utils.remove_unwanted_white(line)
            if row == '' or len(row) < 1 or row[0] == '#':
                continue
            cols = row.split('`')
            if len(cols) < 5:
                raise Exception('Something wrong with the stocks.txt file.Check it.')
            ticker = cols[0]
            tickers_list.append(ticker)
            name = cols[1]
            low = float(cols[2])
            high = float(cols[3])
            delta = float(cols[4])
            self.stocks_instances.append(stock.Stock(ticker, name, low, high, delta))
        self.tickers = ','.join(tickers_list)

    def processAllStocks(self):        
        email_text = ''
        for stock_instance in self.stocks_instances:
            ticker = stock_instance.ticker
            price = yf.Ticker(ticker).info['ask']
            self.logger.info('Price of ticker %s is %d' %(ticker, price))
            if price < stock_instance.low:
                email_text += 'Price of %s is lower than %d' %(stock_instance.name, stock_instance.low)
                stock_instance.low = price - stock_instance.delta
		stock_instance.high = price + (2 * stock_instance.delta)
            if price > stock_instance.high:
                email_text += 'Price of %s is higher than %d' %(stock_instance.name, stock_instance.high)
                stock_instance.high = price + stock_instance.delta
		stock_instance.low = price - (2 * stock_instance.delta)
        return email_text
