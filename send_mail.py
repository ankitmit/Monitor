import smtplib

class SendMailServer:
  def __init__(self, port, provider):
    self.port = port
    self.provider = provider

    server = smtplib.SMTP_SSL(provider, port)
    server.login('crackcat2k11', 'ankitmittalbgh')

    
  def SendMail(self, email_text):
    self.server.sendmail('crackcat2k11@gmail.com', 'crackcat2k11@gmail.com', email_text)