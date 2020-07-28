import dropbox

class DropBoxException(Exception):
    pass

class DropBox():
    def __init__(self):
        auth_token = 'e7pGKdpUoZAAAAAAAAADuBcRACZa_d_1Imqny6VuDflqzGCyQ0dAyEUbHp8954xZ'
        self.dbx = dropbox.Dropbox(auth_token)
        self.dbx.users_get_current_account()

    def getFileFromDropBox(self, last_modified, logger):
        file_changed = False
        data = ''
        path = '/Finance/stocks.txt'
        last_modified_date_time = self.dbx.files_get_metadata(path).client_modified
        if last_modified is None or last_modified_date_time > last_modified:
            logger.info('Dropbox file changed.Reading new file')
            try:
                md, res = self.dbx.files_download(path)
            except dropbox.exceptions.HttpError as err:
                logger.info('*** HTTP error Dropbox specific exception', err)
                #raise DropBoxException('Unable to read file from dropbox')
            except Exception as err:
                logger.info('*** Dropbox general Exception : %s', err)
                #raise DropBoxException('DropBoxException happened while reading file from Dropbox')
            data = res.content
            file_changed = True
            last_modified = last_modified_date_time
        return file_changed, data, last_modified

    def uploadFileToDropBox(self, logger, text):
        logger.info('Uploading file to dropbox')
        mode = (dropbox.files.WriteMode.overwrite)
        path = '/Finance/stocks.txt'
        try:
            res = self.dbx.files_upload(text, path, mode)
        except Exception as err:
            logger.info("Exception trying to upload file to dropox: %s", err)
            #raise DropBoxException('DropBoxException happened while writing file to Dropbox')
