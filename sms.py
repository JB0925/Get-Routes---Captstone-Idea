import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from decouple import config

EMAIL = config('EMAIL')
PASSWORD = config('PASSWORD')


def send(message, address):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(EMAIL, PASSWORD)

    msg = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = address
    msg['Subject'] = 'Ride Finder - Reset Password'
    msg.attach(MIMEText(message, 'plain'))
    sms = msg.as_string()


    server.sendmail(EMAIL, address, sms)
    msg = ''
    server.quit()