import logging
import json
from pathlib import Path
from typing import Optional

# Data
from bot.Data.Pack import Pack
from bot.Data.Card import Card
from bot.Data.User import User

class DataDriver:
    def __init__(self, logs_handler):
        self.logger = logging.getLogger("DataDriver")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.logger.addHandler(logs_handler)

        self.config = {}

        self.cards = []
        self.packs = []
        self.users = []
        
        self.card_map = {}

    def initialize_database(self):
        self.logger.info("Initializing database...")

        # Cards
        cards_data = []
        for file in Path("data/cards").glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                cards_data.append(json.load(f))

        for data in cards_data:
            self.cards = self.cards + self.deserialize_cards(data)

        self.card_map = {card.name: card for card in self.cards}
        
        self.logger.info(f"Loaded {len(self.cards)} cards")
        
        # Packs
        packs_data = []
        for file in Path("data/packs").glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                packs_data.append(json.load(f))
        
        for data in packs_data:
            self.packs = self.packs + self.deserialize_packs(data)
        
        self.logger.info(f"Loaded {len(self.packs)} packs")

        # Users
        users_data = []
        for file in Path("data/users").glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                users_data.append(json.load(f))

        for data in users_data:
            self.users.append(User.from_json(data))
        
        self.logger.info(f"Loaded {len(self.users)} users")

    def deserialize_cards(self, data: dict) -> list:
        cards = []
        for bundle in data.values():
            bundle_name = bundle["name"]
            for collection in bundle["collections"]:
                collection_name = collection["name"]
                for card_data in collection["cards"]:
                    card = Card.from_json(
                        data=card_data, 
                        bundle_name=bundle_name,
                        collection_name=collection_name
                        )
                    cards.append(card)
        return cards

    def deserialize_packs(self, data: dict) -> list:
        packs = []
        for pack_data in data.values():
            pack_name = pack_data["name"]
            pack_type = pack_data["type"]

            cards = []
            if pack_type == "all":
                cards = self.get_all_cards()
                pass
            elif pack_type == "bundle":
                cards = self.get_cards_by_bundle(pack_data["bundle_name"])
                pass
            elif pack_type == "collection":
                cards = self.get_cards_by_collection(pack_data["collection_name"])
                pass
            elif pack_type == "custom":
                card_names = pack_data["cards"]
                for name in card_names:
                    card = self.get_card_by_name(name)
                    if card is None:
                        self.logger.warning(f"Pack '{pack_name}': Card '{name}' not found. Skipping")
                        continue
                    cards.append(card)
                pass
            else:
                self.logger.warning(f"Pack '{pack_name}': Invalid pack type '{pack_type}'. Skipping")
                continue

            if cards is None:
                self.logger.warning(f"Pack '{pack_name}': Got empty cards list. Skipping")
                continue

            card_names = []
            for card in cards:
                card_names.append(card.name)
                
            pack = Pack(name=pack_name, card_names=card_names)
            packs.append(pack)

        return packs
    
    def deserialize_users(self, data: dict) -> list:
        users = []
        return users
    
    def load_config(self) -> dict:
        return {}

    def create_user(self, user_id):
        user = User(user_id=user_id)
        self.users.append(user)
        self.save_user(user.id)
        self.logger.info(f"Created user {user.id} and saved to database")

    def save_user(self, user_id):
        user = self.get_user(user_id)
        if user is not None:
            json_data = user.to_json()

            with open(f"data/users/{user.id}.json", "w", encoding="utf-8") as file:
                json.dump(json_data, file, indent=4, ensure_ascii=False)

    def user_exist(self, user_id) -> bool:
        return any(user.id == user_id for user in self.users)
    
    def get_user(self, user_id) -> Optional[User]:
        for user in self.users:
            if user.id == user_id:
                return user
            
        return None

    def get_cards_count(self):
        return len(self.cards)

    def get_bundles_count(self):
        pass

    def get_collection(self):
        pass

    def get_pack_by_name(self, name:str) -> Optional[Pack]:
        for pack in self.packs:
            if pack.name == name:
                return pack
            
        return None
    
    def get_all_cards(self) -> list:
        return self.cards
    
    def get_cards_by_bundle(self, bundle_name:str) -> Optional[list]:
        cards = []
        for card in self.cards:
            if card.bundle == bundle_name:
                cards.append(card)

        return cards

    def get_cards_by_collection(self, collection_name:str) -> Optional[list]:
        cards = []
        for card in self.cards:
            if card.collection == collection_name:
                cards.append(card)

        return cards

    def get_cards_from_list(self, card_list:list) -> list:
        cards = []
        for card_name in card_list:
            card = self.get_card_by_name(card_name)
            if card is not None:
                cards.append(card)

        return cards
    
    def get_card_by_name(self, name) -> Optional[Card]:
        return self.card_map.get(name)
