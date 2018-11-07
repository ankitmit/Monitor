import smtplib
 
def SendMail(email_text, port, provider):
  server = smtplib.SMTP_SSL(provider, port)
  server.login('crackcat2k11', 'ankitmittalbgh')
  server.sendmail('crackcat2k11@gmail.com', 'crackcat2k11@gmail.com', email_text)
