import smtplib

class SendMailServer:
  def __init__(self, to, port, provider):
    self.to = to
    self.port = port
    self.provider = provider

    server = smtplib.SMTP_SSL(provider, port)
    server.login('crackcat2k11', 'ankitmittalbgh')

    
  def SendMail(self, email_text, to):
    self.server.sendmail('crackcat2k11@gmail.com', to, email_text)