from typing import List
from dataclasses import dataclass

@dataclass
class StickerModel:
    id: int
    slot: int
    icon_url: str
    name: str
    price: float
    
    def __init__(self):
        self.id = 0
        self.slot = 0
        self.icon_url = ""
        self.name = ""
        self.price = 0.00

    def to_dict(self):
        return {
            "id": self.id,
            "slot": self.slot,
            "icon_url": self.icon_url,
            "name": self.name,
            "price": self.price
        }
    
@dataclass
class SkinChanges:
    added: bool
    removed: bool
    priceChanged: bool
    oldPrice: float
    newPrice: float

    def __init__(self):
        self.added = False
        self.removed = False
        self.priceChanged = False
        self.oldPrice = 0.00
        self.newPrice = 0.00

    def to_dict(self):
        return {
            "added": self.added,
            "removed": self.removed,
            "priceChanged": self.priceChanged,
            "oldPrice": self.oldPrice,
            "newPrice": self.newPrice
        }
    
@dataclass
class SkinModel:
    id: int
    price: float
    paint_seed: int
    float_value: float
    item_name: str
    wear_name: str
    description: str
    inspect_link: str
    is_stattrak: bool
    is_souvenir: bool
    screenshot_id: int
    stickers: List[StickerModel]
    skinChanges: SkinChanges
    
    def __init__(self):
        self.id = 0
        self.price = 0.00
        self.paint_seed = 0
        self.float_value = 0.00
        self.item_name = ""
        self.wear_name = ""
        self.description = ""
        self.inspect_link = ""
        self.is_stattrak = False
        self.is_souvenir = False
        screenshot_id = 0
        self.stickers = list()
        self.skinChanges = SkinChanges()

    def to_dict(self): # Helper to convert object to dictionary for JSON serialization
        return  {
            "id": self.id,
            "price": self.price,
            "paint_seed": self.paint_seed,
            "float_value": self.float_value,
            "item_name": self.item_name,
            "wear_name": self.wear_name,
            "description": self.description,
            "inspect_link": self.inspect_link,
            "is_stattrak": self.is_stattrak,
            "is_souvenir": self.is_souvenir,
            "screenshot_id": self.screenshot_id,
            "stickers": [obj.to_dict() for obj in self.stickers],
            "skinChanges": self.skinChanges.to_dict()
        }