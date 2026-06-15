from bot.Utils.Enums import RARITY_WEIGHT
import random

class Pack:
    def __init__(self, name:str, card_names):
        self.name = name
        self.card_names = card_names