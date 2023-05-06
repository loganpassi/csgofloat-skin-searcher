class SkinModel:
    id: str
    price: int
    paint_seed: int
    float_value: float
    item_name: str
    wear_name: str
    description: str
    inspect_link: str
    is_stattrak: bool
    is_souvenir: bool
    
    def __init__(self):
        self.id = ""
        self.price = 0
        self.paint_seed = 0
        self.float_value = 0.0
        self.item_name = ""
        self.wear_name = ""
        self.description = ""
        self.inspect_link = ""
        self.is_stattrak = False
        self.is_souvenir = False
    