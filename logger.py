import requests
import os
import json
import time
import smtplib
import dropbox_wrapper
import re
import datetime
import logging
import pytz

def getFileFromDropBox():
    data = ''
    auth_token = 'e7pGKdpUoZAAAAAAAAABcX28r0cul9w9slEQyuaAutv88eJc7Qz0ta8wxak2bguO'
    dbx = dropbox_wrapper.Dropbox(auth_token)
    dbx.users_get_current_account()
    path = '/Finance/records.txt'
    try:
        md, res = dbx.files_download(path)
    except dropbox_wrapper.exceptions.HttpError as err:
        logger.info('*** HTTP error', err)
        return None
    data = res.content
    print data