import smtplib
import os
import math,random
from datetime import datetime, timedelta
import re

from .models import OTP

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_DOMAIN = os.getenv("EMAIL_DOMAIN")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))

def send_email(receiver: str, message: str):
    """
    send message (str) to receiver (str, coma separated if multiples)
    """

    s = smtplib.SMTP(EMAIL_DOMAIN, EMAIL_PORT)       
    s.connect(EMAIL_DOMAIN, EMAIL_PORT)                                                     
    s.starttls()                                                                                       
    s.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
    s.sendmail(EMAIL_ADDRESS, receiver, message)
    s.quit()

def handle_otp(receiver: str) -> tuple:
    """
    handle email domain verification, OTP generation and sending
    """

    allowed_domains = [
        'isep.fr',
        'eleve.isep.fr',
        'ext.isep.fr'
    ]

    # check if email is valid
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if not re.fullmatch(regex, receiver):
        return None, -2

    # Check if email domain is allowed
    if receiver.split('@')[-1] not in allowed_domains:
        return None,-1

    # Generate 6 digit OTP
    digits = "0123456789"
    otp = ""
    for i in range(6) :
        otp += digits[math.floor(random.random() * 10)]

    # Store the OTP in the database
    now = datetime.now()
    OTP.objects.create(code = otp, email = receiver, created_at = now, expiration = now + timedelta(minutes = 10))

    # create message and send email
    name = receiver.split('@')[0]
    message = f"""Subject: Your Oboo validation code\n\n
Hello {name},

Here is your Oboo One Time Password (OTP):

{otp}

It will expire in 10 minutes.

Have a good day :)
"""

    send_email(receiver,message)
    print(f"Successfully sent email to {receiver}  with OTP : {otp}")
    return otp,0
