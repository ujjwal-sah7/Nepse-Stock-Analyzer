import smtplib
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(receiver_email, stock_name, price):

    sender_email = st.secrets["EMAIL_USER"]
    sender_password = st.secrets["EMAIL_PASS"]

    subject = f"Stock Alert for {stock_name}"

    body = f"""
Hello,

Stock Alert!

{stock_name} price has reached {price}.

Check the market now.

Thank you.
"""

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)

    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)

    server.quit()