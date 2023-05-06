from requests.auth import HTTPBasicAuth
import requests

from models import SkinModel

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