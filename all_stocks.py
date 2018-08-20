import utils
import requests
import json
import stock

BASE_URL = 'https://api.iextrading.com/1.0/stock/market/batch?types=quote&symbols='

def _GetCurrentPrice(url, logger):
    json_obj_list = {}
    try:
        myResponse = requests.get(url)
        cont = myResponse.content
        if myResponse.ok:
            json_obj_list = json.loads(cont)

    except:
        logger.info("Shit broke while getting prices.")
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
        request_url = BASE_URL + self.tickers
        price_json = _GetCurrentPrice(request_url, self.logger)
        email_text = ''
        for stock_instance in self.stocks_instances:
            ticker = stock_instance.ticker
            price = float(price_json[ticker]["quote"]["latestPrice"])
            if price < stock_instance.low:
                email_text += 'Price of %s is lower than %d' %(stock_instance.name, stock_instance.low)
                stock_instance.low -= stock_instance.delta
            if price > stock_instance.high:
                email_text += 'Price of %s is higher than %d' %(stock_instance.name, stock_instance.high)
                stock_instance.high += stock_instance.delta
        return email_text
