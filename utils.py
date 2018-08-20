import re
import datetime
import pytz
import logging

def remove_unwanted_white(str):
    str = re.sub("\s\s+" , " ", str)
    str = str.rstrip()
    str = str.lstrip()
    return str

def getCurrentHourAndMinutes():
    curr = datetime.datetime.now(pytz.timezone('US/Eastern'))
    return curr.hour, curr.minute


def createLoggerInstance():
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
    return logger