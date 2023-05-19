from email.mime.text import MIMEText
from typing import List
from datetime import datetime
import requests
import smtplib
import json
import time

from models import SkinModel, StickerModel

def main():
    
    jsonFile = open('./settings.json')
    settings = json.load(jsonFile)
    emailSettings = settings["emailSettings"]
    searchSettings = settings["searchSettings"]
    
    queryParams = "sort_by=" + searchSettings["sortBy"] + "&min_float=" + str(searchSettings["minFloat"]) + "&max_float=" + str(searchSettings["maxFloat"]) + searchSettings["skinParams"]

    apiUrl = searchSettings["baseApiUrl"] + queryParams
    searchUrl = searchSettings["baseSearchUrl"] + queryParams
    headers = {'Accept': 'application/json'}
    
    savedSkins:List[SkinModel] = list()
    foundSkins:List[SkinModel] = list()
    
    while(True):

        try:
            response = requests.get(apiUrl, headers=headers)
        except:
            print("Get Request Failed")
        
        if(response.status_code != 200):
            print("Get Request Failed: " + response.reason)

        if(len(response.json()) > 0):
            
            foundSkins = list()
            
            for obj in response.json():
                skin = obj["item"]
                currentSkin = SkinModel()
                currentSkin.id = int(obj["id"])
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
                    

                foundSkins.append(currentSkin)
        
        if(len(foundSkins) > 0 and len(savedSkins) == 0):
            savedSkins = foundSkins
            prepareAndSendEmail(savedSkins, emailSettings, searchUrl)
        elif(len(foundSkins) != len(savedSkins)):
            savedSkins = foundSkins
            prepareAndSendEmail(savedSkins, emailSettings, searchUrl)
        elif(not compareLists(foundSkins, savedSkins)):
            savedSkins = foundSkins
            prepareAndSendEmail(savedSkins, emailSettings, searchUrl)
        
        print("Sleeping...")
        
        #Sleep for 15 min (900 sec)
        time.sleep(900)


def compareLists(foundSkins: List[SkinModel], savedSkins: List[SkinModel]) -> bool:
    for i in range(len(foundSkins)):
        if(foundSkins[i].id != savedSkins[i].id):
            return False
        elif(foundSkins[i].price != savedSkins[i].price):
            return False
        
    return True

def prepareAndSendEmail(skinList: List[SkinModel], emailSettings, searchUrl) -> None:
    if(len(skinList) > 0):
        print("Skins found, preparing email")
        
        links = ""
        
        for skin in skinList:
            links += "<div><ul><li>Float: " + str(skin.float_value) + "</li><li>Price: " + str('${:,.2f}'.format(skin.price)) + "</li></ul></div>"
        
        subject = "Skins Found @ " + datetime.now().strftime("%m/%d/%Y %I:%M %p")
        body = "<html><body><h1>Search Link: <a href=\"" + searchUrl + "\">" + searchUrl + "</a><br><br>" + links + "</body></html>"
        sender = emailSettings["sender"]
        recipients = emailSettings["recipients"]
        password = emailSettings["password"]

        sendEmail(subject, body, sender, recipients, password)
    else:
        print("No skins found")

def sendEmail(subject, body, sender, recipients, password) -> None:
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
