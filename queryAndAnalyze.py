import time
import all_stocks
import dropbox_wrapper
import utils
import send_mail

SEP = '`'
NEW_LINE = '\n'


def writeFileWithNewPrices(stocks, dropbox_instance):
    text = ''
    for stock in stocks:
        text += stock.ticker + SEP + stock.name + SEP + str(stock.low) \
                + SEP + str(stock.high) + SEP + str(stock.delta) + NEW_LINE
    text = text[:-1]
    dropbox_instance.uploadFileToDropBox(text)

def mainFunc() :
    dropbox_instance = dropbox_wrapper.DropBox()
    logger = utils.createLoggerInstance()
    last_modified = None
    stocks = all_stocks.AllStocks(logger)
    file_changed, data, last_modified = dropbox_instance.getFileFromDropBox(last_modified, logger)
    stocks.populateAllStocks(data)
    send_mail_server = send_mail.SendMailServer()
    while True:
        hour, minute = utils.getCurrentHourAndMinutes()
        if hour > 16:
            logger.info("Martkets are closed. Exiting the script now")
            time.sleep(600)
            continue
        if hour < 9 or (hour == 9 and minute < 30):
            logger.info("Martkets are not yet open.Continue")
            time.sleep(600)
            continue
        file_changed, data, last_modified = dropbox_instance.getFileFromDropBox(last_modified, logger)
        if file_changed:
            stocks.populateAllStocks(data)
        email_text = stocks.processAllStocks()
        if email_text != '' and len(email_text) > 0:
            logger.info('sending email')
            send_mail_server.SendMail(email_text, 'crackcat2k11@gmail.com')
            writeFileWithNewPrices(stocks, dropbox_instance)
    time.sleep(120)

mainFunc()
