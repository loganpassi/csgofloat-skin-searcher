from typing import List

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
    stickers: List[StickerModel]
    
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
        self.stickers = list()
