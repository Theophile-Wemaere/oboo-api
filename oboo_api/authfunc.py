import smtplib
import os
import math,random
from datetime import datetime, timedelta
import re

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_DOMAIN = os.getenv("EMAIL_DOMAIN")
EMAIL_PORT = os.getenv("EMAIL_PORT")

def send_email(receiver:str,message:str):
    """
    send message (str) to receiver (str, coma separated if multiples)
    """

    s = smtplib.SMTP(EMAIL_DOMAIN, EMAIL_PORT)       
    s.connect(EMAIL_DOMAIN, EMAIL_PORT)                                                     
    s.starttls()                                                                                       
    s.login(EMAIL_ADDRESS,EMAIL_PASSWORD)                                                                         
    s.sendmail(EMAIL_ADDRESS, receiver, message)                                                     
    s.quit()

def handle_otp(receiver:str)->tuple:
    """
    handle email domain verification, OTP generation and sending
    """

    allowed_domains = [
        'isep.fr',
        'eleve.isep.fr',
        'external.isep.fr'
    ]

    # check if email is valid
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if not re.fullmatch(regex, receiver):
        return None, -2

    # check if email is allowed
    if receiver.split('@')[-1] not in allowed_domains:
        return None,-1

    # generate 6 digit OTP
    digits = "0123456789"
    otp = ""
    for i in range(6) :
        otp += digits[math.floor(random.random() * 10)]

    # TODO : store OTP, expiration and creator email in database
    current_datetime = datetime.now()
    otp_expiration = current_datetime + timedelta(minutes = 10)
    # database.store(otp,otp_expiration,receiver)

    # create message and send email
    name = receiver.split('@')[0]
    message = f"""
To: {name} <{receiver}>
Subject: Oboo - Your One Time Password

Hello {name},

Here is your One Time Password (OTP) for Oboo mobile app :
<br>
<center><h2>{otp}</h2></center>
<br>

It will expire in 10 minutes.

Have a good day :)
"""

    send_email(receiver,message)
    print(f"Successfully sent email to {receiver}  with OTP : {otp}")
    return otp,0