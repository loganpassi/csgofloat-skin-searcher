from email.mime.text import MIMEText
from typing import List
from datetime import datetime
from dataclasses import dataclass, asdict
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
                    savedSkinsDict = json.load(file)["data"]
                    savedSkins = convertDictListToSkinList(savedSkinsDict)
            except Exception as e:
                print(f"Error while opening file: {e}")
        elif(not os.path.exists(savedSkinsFilePath)):
            try:
                # If file does not exist, create it
                with open(savedSkinsFileName, 'w') as file:
                    file.write("")
            except Exception as e:
                print(f"Error while writing to file: {e}")

        savedSkinsJson = {"data": [asdict(obj) for obj in foundSkins]}

        if(len(foundSkins) > 0 and len(savedSkins) == 0):
            writeToFile(savedSkinsJson, savedSkinsFileName)
            prepareAndSendEmail(foundSkins, emailSettings, searchUrl, baseItemLink, playsideLink, backsideLink)
        else:
            changesMade, skinChanges = compareLists(foundSkins, savedSkins)
            if(changesMade):
                writeToFile(savedSkinsJson, savedSkinsFileName)
                prepareAndSendEmail(skinChanges, emailSettings, searchUrl, baseItemLink, playsideLink, backsideLink)
        
        print("Sleeping...")
        
        # Sleep for 15 min (900 sec)
        time.sleep(900)

def convertDictListToStickerList(dictList) -> List[StickerModel]:
    stickerList:List[SkinModel] =  list()
    for d in dictList:
        sticker = StickerModel()
        sticker.id = d["id"]
        sticker.slot = d["slot"]
        sticker.icon_url = d["icon_url"]
        sticker.name = d["name"]
        sticker.price = d["price"]
        stickerList.append(sticker)
    return stickerList

def convertDictListToSkinList(dictList) -> List[SkinModel]:
    skinList:List[SkinModel] = list()
    for d in dictList:
        skin = SkinModel()
        skin.id = d["id"]
        skin.price = d["price"]
        skin.paint_seed = d["paint_seed"]
        skin.float_value = d["float_value"]
        skin.item_name = d["item_name"]
        skin.wear_name = d["wear_name"]
        skin.description = d["description"]
        skin.inspect_link = d["inspect_link"]
        skin.is_stattrak = d["is_stattrak"]
        skin.is_souvenir = d["is_souvenir"]
        skin.screenshot_id = d["screenshot_id"]
        skin.stickers = convertDictListToStickerList(d["stickers"])
        skinList.append(skin)
    return skinList

def writeToFile(string, savedSkinsFileName):
    try:
        print("Writing to file...")
        # This will overwrite file content
        with open(savedSkinsFileName, 'w') as file:
            json.dump(string, file, indent=4)
    except Exception as e:
        print(f"Error while writing to file: {e}")

    print("File updated!")

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
            if "cs2_screenshot_id" in skin:
                currentSkin.screenshot_id = skin["cs2_screenshot_id"]
            else:
                currentSkin.screenshot_id = "0"
            
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

def compareLists(foundSkins: List[SkinModel], savedSkins: List[SkinModel]):
    changesMade = False
    skinChanges:List[SkinModel] = list()

    # Loop through skins in savedSkins
    for skin in savedSkins:
        skinChange = skin
        foundSkinsIndex = next((i for i, obj in enumerate(foundSkins) if skin.id == obj.id), -1)
        if(foundSkinsIndex == -1): # Saved skin is no longer in the found skins, i.e. removed
            skinChange.skinChanges.removed = True
            changesMade = True
        else: # Index of skin was found, need to check if price has changed
             foundSkin = foundSkins[foundSkinsIndex]
             if(skin.price != foundSkin.price):
                 skinChange.skinChanges.oldPrice = skin.price
                 skinChange.skinChanges.newPrice = foundSkin.price
                 skinChange.skinChanges.priceChanged = True
                 changesMade = True
        
        # Append skinChange to skinChanges list
        skinChanges.append(skinChange)

        # If foundSkinsIndex != -1 we want to remove that element from the list
        # This will allow us to see what new skins were found that dont exist in the savedSkins list
        if(foundSkinsIndex != -1):
            del foundSkins[foundSkinsIndex]

    # Check if any skins left in found skins, if so they will be added to skinChanges with prop added = true
    if(len(foundSkins) > 0):
        for skin in foundSkins:
            skinChange = skin
            skinChange.skinChanges.added = True
            skinChanges.append(skinChange)
            changesMade = True
        # Need to sort list by float in asc order
        skinChanges.sort(key=lambda x: x.float_value)
        
    return changesMade, skinChanges

def prepareAndSendEmail(skinList: List[SkinModel], emailSettings, searchUrl, baseItemLink, playsideLink, backsideLink) -> None:
    if(len(skinList) > 0):
        print("Skins found, preparing email")
        
        links = ""
        
        for skin in skinList:
            fontColor = "black"
            if(skin.skinChanges.added):
                fontColor = "green"
            elif(skin.skinChanges.removed):
                fontColor = "red"
            elif(skin.skinChanges.priceChanged):
                fontColor = "purple"
            itemLink = baseItemLink + str(skin.id)
            playside = str(playsideLink).replace("$skinId", str(skin.screenshot_id))
            backside = str(backsideLink).replace("$skinId", str(skin.screenshot_id))
            floatHtml = "<li>Float: " + str(skin.float_value) + "</li>"
            priceHtml = ""
            if(skin.skinChanges.priceChanged):
                priceHtml = "<li>Price: " + str('${:,.2f}'.format(skin.skinChanges.oldPrice)) + "-->" + str('${:,.2f}'.format(skin.skinChanges.newPrice)) + "</li>"
            else:
                priceHtml = "<li>Price: " + str('${:,.2f}'.format(skin.price)) + "</li>"

            linkHtml = "<li>Link: <a href=\"" + str(itemLink)  + "\">" + itemLink  + "</a></li>"
            playSideHtml = "<img style=\"height: 20%; width: 20%;\" src=\"" + playside + "\">"
            backSideHtml = "<img style=\"height: 20%; width: 20%;\" src=\"" + backside + "\">"
            links += f"<div style=\"display: flex; align-items: center; color: {fontColor};\"><ul>" + floatHtml + priceHtml + linkHtml + "</ul>" + playSideHtml + backSideHtml + "</div>"
        
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
