from email.mime.text import MIMEText
from typing import List
from datetime import datetime
import requests
import smtplib
import json
import time
import os
import sys

from models import SkinModel, StickerModel

def main():

    script_path = os.path.abspath(__file__)
    script_directory = os.path.dirname(script_path)
    jsonFile = open(script_directory + '/settings.json')
    settings = json.load(jsonFile)
    authorizationSettings = settings["authorization"]
    emailSettings = settings["emailSettings"]
    searchSettings = settings["searchSettings"]
    savedSkinsFileName = "savedSkins.json"
    savedSkinsFilePath = script_directory + "/" + savedSkinsFileName
    
    queryParams = "sort_by=" + searchSettings["sortBy"] + "&min_float=" + str(searchSettings["minFloat"]) + "&max_float=" + str(searchSettings["maxFloat"]) + searchSettings["skinParams"]

    apiUrl = searchSettings["baseApiUrl"] + queryParams
    searchUrl = searchSettings["baseSearchUrl"] + queryParams
    baseItemLink = searchSettings["baseItemLink"]
    playsideLink = searchSettings["playsideLink"]
    backsideLink = searchSettings["backsideLink"]

    headers = {
        'Accept': 'application/json',
        'Authorization': authorizationSettings["apiKey"]
    }
    
    savedSkins:List[SkinModel] = list()
    foundSkins:List[SkinModel] = list()
    
    while(True):

        try:
            response = requests.get(apiUrl, headers=headers)
        except:
            print("Get Request Failed")
            sys.exit(1)
        
        if(response.status_code != 200):
            print("Get Request Failed: " + response.reason)
            sys.exit(1)

        foundSkins = compileList(response.json())

        if(os.path.exists(savedSkinsFilePath) and os.path.getsize(savedSkinsFilePath) > 0):
            try:
                # Store data from text file in savedSkins
                with open(savedSkinsFileName, 'r') as file:
                    savedSkins = json.load(file)["data"]
            except Exception as e:
                print(f"Error while opening file: {e}")
        elif(not os.path.exists(savedSkinsFilePath)):
            try:
                # If file does not exist, create it
                with open(savedSkinsFileName, 'w') as file:
                    file.write("")
            except Exception as e:
                print(f"Error while writing to file: {e}")
        
        if(len(foundSkins) > 0 and len(savedSkins) == 0):
            savedSkins = foundSkins
            prepareAndSendEmail(savedSkins, emailSettings, searchUrl, baseItemLink, playsideLink, backsideLink)
        elif(len(foundSkins) != len(savedSkins)):
            savedSkins = foundSkins
            prepareAndSendEmail(savedSkins, emailSettings, searchUrl, baseItemLink, playsideLink, backsideLink)
        elif(not compareLists(foundSkins, savedSkins)):
            savedSkins = foundSkins
            prepareAndSendEmail(savedSkins, emailSettings, searchUrl, baseItemLink, playsideLink, backsideLink)

        print ("Writing to file...")

        savedSkinsJson = {"data": [obj.to_dict() for obj in foundSkins]}
        writeToFile(savedSkinsJson, savedSkinsFileName)
        
        print("Sleeping...")
        
        # Sleep for 15 min (900 sec)
        time.sleep(900)

def writeToFile(string, savedSkinsFileName):
    with open(savedSkinsFileName, 'w') as file:
        json.dump(string, file, indent=4)

def compileList(json) -> List[SkinModel]:

    skinList = list()

    if(len(json) > 0):

        for obj in json["data"]:
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
            currentSkin.screenshot_id = skin["cs2_screenshot_id"]
            
            if "stickers" in skin:
                for sticker in skin["stickers"]:
                    currentSticker = StickerModel()
                    currentSticker.id = sticker["stickerId"]
                    currentSticker.slot = sticker["slot"]
                    currentSticker.icon_url = sticker["icon_url"]
                    currentSticker.name = sticker["name"]
                    currentSticker.price = float(int(sticker["reference"]["price"])/100)
                    
                    currentSkin.stickers.append(currentSticker)
                
            skinList.append(currentSkin)

    return skinList
            


def compareLists(foundSkins: List[SkinModel], savedSkins: List[SkinModel]) -> bool:
    for i in range(len(foundSkins)):
        if(foundSkins[i].id != savedSkins[i]["id"]):
            return False
        elif(foundSkins[i].price != savedSkins[i]["price"]):
            return False
        
    return True

def prepareAndSendEmail(skinList: List[SkinModel], emailSettings, searchUrl, baseItemLink, playsideLink, backsideLink) -> None:
    if(len(skinList) > 0):
        print("Skins found, preparing email")
        
        links = ""
        
        for skin in skinList:
            itemLink = baseItemLink + str(skin.id)
            playside = str(playsideLink).replace("$skinId", str(skin.screenshot_id))
            backside = str(backsideLink).replace("$skinId", str(skin.screenshot_id))
            links += "<div style=\"display: flex; align-items: center;\">" + "<ul><li>Float: " + str(skin.float_value) + "</li><li>Price: " + str('${:,.2f}'.format(skin.price)) + "</li><li>Link: <a href=\"" + str(itemLink)  + "\">" + itemLink  + "</a></li></ul>" + "<img style=\"height: 20%; width: 20%;\" src=\"" + playside + "\"><img style=\"height: 20%; width: 20%;\" src=\"" + backside + "\"></div>"
        
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
    except Exception as e:
        print(f"Failed to send email: {e}")
        
    smtp_server.quit()

if __name__ == "__main__":
    main()
