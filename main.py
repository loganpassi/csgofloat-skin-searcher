from requests.auth import HTTPBasicAuth
from email.mime.text import MIMEText
import requests
import smtplib

from models import SkinModel

import smtplib
from email.mime.text import MIMEText

def main():
    subject = "Email Subject"
    body = "This is the body of the text message"
    sender = "sender@gmail.com"
    recipients = ["recipient1@gmail.com", "recipient2@gmail.com"]
    password = "password"

    send_email(subject, body, sender, recipients, password)

    url = 'https://csgofloat.com/api/v1/listings?limit=30&def_index=5030&paint_index=10018'
    headers = {'Accept': 'application/json'}

    maxFloat = 0.20

    try:
        response = requests.get(url, headers=headers)
    except:
        print("Get Request Failed")


    skins = []

    for s in response.json():
        if float(s["item"]["float_value"]) <= maxFloat:
            currentSkin = SkinModel()
            currentSkin.id = s["id"]
            currentSkin.price = int(s["price"])
            currentSkin.paint_seed = int(s["item"]["paint_seed"])
            currentSkin.float_value = float(s["item"]["float_value"])
            currentSkin.item_name = s["item"]["item_name"]
            currentSkin.wear_name = s["item"]["wear_name"]
            currentSkin.description = s["item"]["description"]
            currentSkin.inspect_link = s["item"]["inspect_link"] if "inspect_link" in s else ""
            currentSkin.is_stattrak = s["item"]["is_stattrak"]
            currentSkin.is_souvenir = s["item"]["is_souvenir"]

            skins.append(currentSkin)

    print("end")

def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    
    try:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    except:
        print("Failed to send email")
        
    smtp_server.quit()


if __name__ == "__main__":
    main()
