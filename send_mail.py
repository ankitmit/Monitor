import smtplib
class SendMail:
  def __init__(self, from, to, port, provider):
    self.from = from
    self.to = to
    self.port = port
    self.provider = provider
    
  def SendMail(self)
    server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)
    server.login(gmail_user, password)
    server.sendmail(gmail_user, TO, email_text)
    server.quit()
