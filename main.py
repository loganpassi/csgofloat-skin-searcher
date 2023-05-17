from requests.auth import HTTPBasicAuth
from email.mime.text import MIMEText
import requests
import smtplib
import json

from models import SkinModel

import smtplib
from email.mime.text import MIMEText

def main():
    
    jsonFile = open('./settings.json')
    settings = json.load(jsonFile)
    emailSettings = settings["emailSettings"]
    searchSettings = settings["searchSettings"]

    url = searchSettings["searchUrl"]
    headers = {'Accept': 'application/json'}

    maxFloat = searchSettings["maxFloat"]
    minFloat = searchSettings["minFloat"]

    try:
        response = requests.get(url, headers=headers)
    except:
        print("Get Request Failed")


    skins = []

    for s in response.json():
        if float(s["item"]["float_value"]) <= maxFloat and float(s["item"]["float_value"]) >= minFloat:
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

    if(len(skins) > 0):
        print("Skins found preparing email")
        
        subject = "Email Subject"
        body = "This is the body of the text message"
        sender = emailSettings["sender"]
        recipients = emailSettings["recipients"]
        password = emailSettings["password"]

        send_email(subject, body, sender, recipients, password)
    else:
        print("No skins found")

def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    
    try:
        print("Attempting to send email")
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
        print("Email sent")
    except:
        print("Failed to send email")
        
    smtp_server.quit()


if __name__ == "__main__":
    main()
