from requests.auth import HTTPBasicAuth
from email.mime.text import MIMEText
from typing import List
import requests
import smtplib
import json
import time

from models import SkinModel, StickerModel

import smtplib
from email.mime.text import MIMEText

def main():
    
    jsonFile = open('./settings.json')
    settings = json.load(jsonFile)
    emailSettings = settings["emailSettings"]
    searchSettings = settings["searchSettings"]

    apiUrl = searchSettings["baseApiUrl"] + searchSettings["queryParams"]
    searchUrl = searchSettings["baseSearchUrl"] + "min_float=" + str(searchSettings["minFloat"]) + "&max_float=" + str(searchSettings["maxFloat"]) + searchSettings["queryParams"]
    headers = {'Accept': 'application/json'}

    maxFloat = searchSettings["maxFloat"]
    minFloat = searchSettings["minFloat"]
    
    while(True):

        try:
            response = requests.get(apiUrl, headers=headers)
        except:
            print("Get Request Failed")


        skins:List[SkinModel] = list()

        for obj in response.json():
            skin = obj["item"]
            if float(skin["float_value"]) <= maxFloat and float(skin["float_value"]) >= minFloat:
                currentSkin = SkinModel()
                currentSkin.id = obj["id"]
                currentSkin.price = float(int(obj["price"])/100)
                currentSkin.paint_seed = int(skin["paint_seed"])
                currentSkin.float_value = float(skin["float_value"])
                currentSkin.item_name = skin["item_name"]
                currentSkin.wear_name = skin["wear_name"]
                currentSkin.description = skin["description"]
                currentSkin.inspect_link = skin["inspect_link"] if "inspect_link" in skin else ""
                currentSkin.is_stattrak = skin["is_stattrak"]
                currentSkin.is_souvenir = skin["is_souvenir"]
                
                if "stickers" in skin:
                    for sticker in skin["stickers"]:
                        currentSticker = StickerModel()
                        currentSticker.id = sticker["stickerId"]
                        currentSticker.slot = sticker["slot"]
                        currentSticker.icon_url = sticker["icon_url"]
                        currentSticker.name = sticker["name"]
                        currentSticker.price = float(int(sticker["scm"]["price"])/100)
                        
                        currentSkin.stickers.append(currentSticker)
                    

                skins.append(currentSkin)

        if(len(skins) > 0):
            print("Skin(s) found, preparing email")
            
            links = ""
            
            for skin in skins:
                links += "<div><ul><li>Float: " + str(skin.float_value) + "</li><li>Price: " + str('${:,.2f}'.format(skin.price)) + "</li></ul></div>"
            
            subject = "Skin Searcher"
            body = "<html><body><h1>Search Link: <a href=\"" + searchUrl + "\">" + searchUrl + "</a><br><br>" + links + "</body></html>"
            sender = emailSettings["sender"]
            recipients = emailSettings["recipients"]
            password = emailSettings["password"]

            sendEmail(subject, body, sender, recipients, password)
        else:
            print("No skins found")
        
        print("Sleeping...")
        
        #Sleep for 15 min (900 sec)
        time.sleep(900)

def sendEmail(subject, body, sender, recipients, password):
    msg = MIMEText(body, "html")
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
