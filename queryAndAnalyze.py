import requests
import os
import json
import time
import smtplib
import dropbox
import re
import datetime
import logging
import pytz
# base_url = {}
# base_url['NASDAQ'] = 'https://www.google.com/finance/info?q=NASDAQ%3A'
# base_url['NYSE'] = 'https://www.google.com/finance/info?q=NYSE%3A'
baseUrl = 'https://api.iextrading.com/1.0/stock/market/batch?types=quote&symbols='
last_modified = None
NEW_LINE = '\n'
SEP = '`'

def isConfigFileModified():
    curr_date_time = datetime.datetime.now(pytz.timezone('US/Eastern'))
    
class Stock:
    def __init__(self, ticker, name, market, low, high, delta):
        self.ticker = ticker
        self.market = market
        self.low = low
        self.high = high
        #self.url = url
        self.name = name
        self.delta = delta

class Process:
    def __init__(self):
        self.allStocks = []
        self.tickers = []

    def addStock(self, stock):
        self.allStocks.append(stock)

    def addTicker(self, ticker):
        self.tickers.append(ticker)

    def getAllStocks(self):
        return self.allStocks

    def getAllTickers(self):
        return self.tickers

def remove_unwanted_white(str):
		str = re.sub("\s\s+" , " ", str)
		str = str.rstrip()
		str = str.lstrip()
		return str

def getCurrentHourAndMinutes():
    curr = datetime.datetime.now(pytz.timezone('US/Eastern')) 
    return curr.hour, curr.minute

def createAllStocksNew(txt):
    global pInstance,base_url
    pInstance = Process()
    allRows = txt.split('\n')
    for line in allRows:
        row = remove_unwanted_white(line)
        if row == '' or len(row) < 1 or row[0] == '#':
            continue
        cols = row.split('`')
        ticker = cols[0]
        name = cols[1]
        market = cols[2]
        low = 0
        high = 0
        delta = 0
        if len(cols) > 3:
            low = float(cols[3])
        if len(cols) > 4:
            high = float(cols[4])
        if len(cols) > 5:
            delta = float(cols[5])

        #url = baseUrl + ticker + '/quote'
        pInstance.addStock(Stock(ticker, name, market, low, high, delta))
        pInstance.addTicker(ticker)

    return pInstance

def createAllStocks(txt):
    global pInstance,base_url
    pInstance = Process()
    allRows = txt.split('\n')
    for line in allRows:
        row = remove_unwanted_white(line)
        if row == '' or len(row) < 1 or row[0] == '#':
            continue
        cols = row.split('`')
        ticker = cols[0]
        name = cols[1]
        market = cols[2]
        low = 0
        high = 0
        delta = 0
        if len(cols) > 3:
            low = float(cols[3])
        if len(cols) > 4:
            high = float(cols[4])
        if len(cols) > 5:
            delta = float(cols[5])

        url = baseUrl + ticker + '/quote'
        pInstance.addStock(Stock(ticker, name, market, low, high, url, delta))

    return pInstance

def mainFunc():
    global logger
    while True:
        hour, minute = getCurrentHourAndMinutes()
        if hour > 16:
            logger.info("Martkets are closed. Exiting the script now")
            time.sleep(600)
            continue
        if hour < 9 or (hour == 9 and minute < 30):
            logger.info("Martkets are not yet open.Continue")
            time.sleep(600)
            continue
        file_changed, data = getFileFromDropBox()
        if file_changed:
            pInstance = createAllStocksNew(data)
        email_text, send_mail = processAllStocksNew(pInstance)
        if send_mail and email_text != '' and len(email_text) > 0:
	    logger.info( 'sending email')
            sendMail(email_text)
            writeFileWithNewPrices()
        time.sleep(120)

def writeFileWithNewPrices():
    text = ''
    allStocks = pInstance.getAllStocks()
    for stock in allStocks:
        text += stock.ticker + SEP + stock.name + SEP + stock.market + SEP + str(stock.low) \
                + SEP + str(stock.high) + SEP + str(stock.delta) + NEW_LINE
    text = text[:-1]
    uploadFileToDropBox(text)

def processAllStocks(pInstance):
    global logger
    allStocks = pInstance.getAllStocks()
    email_txt = ''
    send_mail = False
    for stock in allStocks:
        curr_price = getCurrentPrice(stock)
        if curr_price != 0 and curr_price < stock.low:
            logger.info('Current price for ' + stock.ticker + ' is less than minimum price ' + str(stock.low))
            send_mail = True
            email_txt += stock.ticker + ' is below the minimum price ' + str(stock.low) + NEW_LINE
            if stock.delta != 0:
                stock.low = stock.low - stock.delta
            else:
                stock.low = 0.98 * stock.low
        elif curr_price != 0 and curr_price > stock.high:
            send_mail = True
            logger.info('Current price for ' + stock.ticker + ' is more than minimum price ' + str(stock.high))
            email_txt += stock.ticker + ' is above the maximum price ' + str(stock.high) + NEW_LINE
            if stock.delta != 0:
                stock.high = stock.high + stock.delta
            else:
                stock.high = 1.02 * stock.high
    return email_txt, send_mail

def processAllStocksNew(pInstance):
    global logger
    allStocks = pInstance.getAllStocks()
    allStocksUrl = baseUrl + ','.join(pInstance.getAllTickers())
    email_txt = ''
    send_mail = False
    allPricesJson = getCurrentPrice(allStocksUrl)
    for stock in allStocks:
        curr_price = None
        if allPricesJson[stock.ticker] is None:
            logger.info("Price for " + stock.ticker + " is not available")
            continue
        curr_price = allPricesJson[stock.ticker]['quote']['latestPrice']
        if curr_price != 0 and curr_price < stock.low:
            logger.info('Current price for ' + stock.ticker + ' is less than minimum price ' + str(stock.low))
            send_mail = True
            email_txt += stock.ticker + ' is below the minimum price ' + str(stock.low) + NEW_LINE
            if stock.delta != 0:
                stock.low = stock.low - stock.delta
            else:
                stock.low = 0.98 * stock.low
        elif curr_price != 0 and curr_price > stock.high:
            send_mail = True
            logger.info('Current price for ' + stock.ticker + ' is more than minimum price ' + str(stock.high))
            email_txt += stock.ticker + ' is above the maximum price ' + str(stock.high) + NEW_LINE
            if stock.delta != 0:
                stock.high = stock.high + stock.delta
            else:
                stock.high = 1.02 * stock.high
    return email_txt, send_mail

def getCurrentPrice(url):
    json_obj_list = {}
    try:
        myResponse = requests.get(url)
        cont = myResponse.content
        if myResponse.ok:
            json_obj_list = json.loads(cont)

    except:
        logger.info("Shit broke while getting prices.")
        sendMail('Shit broke. Look into it jackass.')
    return json_obj_list

def getFileFromDropBox():
    global last_modified, logger
    file_changed = False
    data = ''
    auth_token = 'e7pGKdpUoZAAAAAAAAABcX28r0cul9w9slEQyuaAutv88eJc7Qz0ta8wxak2bguO'
    dbx = dropbox.Dropbox(auth_token)
    dbx.users_get_current_account()
    path = '/Finance/stocks.txt'
    last_modified_date_time = dbx.files_get_metadata(path).client_modified
    if last_modified is None or last_modified_date_time > last_modified:
        logger.info('Dropbox file changed.Reading new file')
        try:
            md, res = dbx.files_download(path)
        except dropbox.exceptions.HttpError as err:
            logger.info('*** HTTP error', err)
            return None
        data = res.content
        file_changed = True
        last_modified = last_modified_date_time
    return file_changed, data

def uploadFileToDropBox(text):
    logger.info('Uploading file to dropbox')
    auth_token = 'e7pGKdpUoZAAAAAAAAABcX28r0cul9w9slEQyuaAutv88eJc7Qz0ta8wxak2bguO'
    dbx = dropbox.Dropbox(auth_token)
    dbx.users_get_current_account()
    overwrite=True
    mode = (dropbox.files.WriteMode.overwrite
            if overwrite
            else dropbox.files.WriteMode.add)
    path = '/Finance/stocks.txt'  
    try:
        res = dbx.files_upload(
                text, path, mode)
    except Exception, e:
        print 'Error :', e

    #logger.info(res)

def sendMail(email_text):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("crackcat2k11@gmail.com", "ankitmittalbgh")

    server.sendmail("crackcat2k11@gmail.com", "crackcat2k11@gmail.com", email_text)
    server.quit()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('activities.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

sendMail("Test text")
# mainFunc()
