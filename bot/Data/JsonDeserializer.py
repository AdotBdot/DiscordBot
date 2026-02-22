import json

from bot.Data.Card import Card

def read_json(file_path)-> dict:
    with open(file_path) as file:
        data = json.load(file)
        return data
    
def to_card_list(data: dict) -> list:
    cards = []
    for bundle in data.values():
        bundle_name = bundle["bundle_name"]
        for collection in bundle["collections"]:
            collection_name = collection["collection_name"]
            for card_data in collection["cards"]:
                card = Card(
                    name=card_data["name"], 
                    description=card_data["description"], 
                    bundle=bundle_name, 
                    collection=collection_name, 
                    rarity=card_data["rarity"], 
                    image_url=card_data["image_url"])
                cards.append(card)
    return cards