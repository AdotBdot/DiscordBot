import logging
import json
from pathlib import Path
from typing import Optional

class DataDriver:
    def __init__(self, logs_handler):
        self.logger = logging.getLogger("DataDriver")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.logger.addHandler(logs_handler)

        self.config = {}

        self.cards:list = []
        self.packs:list = []
        self.users:list = []
        
        self.card_map:dict = {}
        self.bundle_cache = []
        self.collection_cache = []
        self.tag_cache = []
        self.packs_cache = []

    def initialize_database(self):
        self.logger.info("Initializing database...")

        self.load_cards()
        self.load_packs()
        self.load_users()

    def load_cards(self):
        cards_data = []
        for file in Path("data/cards").glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                cards_data.append(json.load(f))

        for data in cards_data:
            cards = []
            for bundle in data.values():
                if not bundle["name"] in self.bundle_cache: self.bundle_cache.append(bundle["name"])
                for collection in bundle["collections"]:
                    if not collection["name"] in self.collection_cache: self.collection_cache.append(collection["name"])
                    for card in collection["cards"]:
                        card["bundle"] = bundle["name"]
                        card["collection"] = collection["name"]
                        cards.append(card)

                        for tag in card["tags"]:
                            if not tag in self.tag_cache: self.tag_cache.append(tag)

            self.cards = self.cards + cards

        self.card_map = {card["name"]: card for card in self.cards}
        
        self.logger.info(f"Loaded {len(self.cards)} card(s)")

    def load_packs(self):
        def deserialize_packs(data: dict) -> list:
            packs = []
            for pack_data in data.values():
                pack_name = pack_data["name"]
                pack_type = pack_data["type"]

                cards = []
                if pack_type == "all":
                    cards = self.get_all_cards()
                elif pack_type == "bundle":
                    cards = self.get_cards_by_bundle(pack_data["bundle_name"])
                elif pack_type == "collection":
                    cards = self.get_cards_by_collection(pack_data["collection_name"])
                elif pack_type == "custom":
                    card_names = pack_data["cards"]
                    for name in card_names:
                        card = self.get_card_by_name(name)
                        if not card:
                            self.logger.warning(f"Pack '{pack_name}': Card '{name}' not found. Skipping")
                            continue
                        cards.append(card)
                else:
                    self.logger.warning(f"Pack '{pack_name}': Invalid pack type '{pack_type}'. Skipping")
                    continue

                if not cards:
                    self.logger.warning(f"Pack '{pack_name}': Got empty cards list. Skipping")
                    continue

                card_names = []
                for card in cards:
                    card_names.append(card["name"])
                    
                pack = {"name": pack_name, "cards": card_names}
                packs.append(pack)
                self.packs_cache.append(pack["name"])

            return packs

        packs_data = []
        for file in Path("data/packs").glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                packs_data.append(json.load(f))
        
        for data in packs_data:
            self.packs = self.packs + deserialize_packs(data)
        
        self.logger.info(f"Loaded {len(self.packs)} pack(s)")
    
    def load_users(self):
        users_data = []
        for file in Path("data/users").glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                users_data.append(json.load(f))

        for data in users_data:
            self.users.append(data)
        
        self.logger.info(f"Loaded {len(self.users)} user(s)")

    def load_config(self) -> dict:
        return {}

    # ====================
    # User methods
    # ====================

    def create_user(self, user_id: int):
        user = {
            "id": user_id,
            "cards": [],
            "packs": ["Common Pack"],
            "cash": 0,
            "melons": 0
        }

        self.users.append(user)
        self.save_user(user["id"])

        self.logger.info(f"Created user {user["id"]} and saved to database")

    def save_user(self, user_id: int):
        user = self.get_user(user_id)

        if not user:
            self.logger.warning(f"User {user_id} not found.")
            return

        with open(f"data/users/{user["id"]}.json", "w", encoding="utf-8") as file:
            json.dump(user, file, indent=4, ensure_ascii=False)

    def update_users(self):
        for user in self.users:
            self.save_user(user["id"])

        self.users = []
        self.load_users()

    def user_exist(self, user_id: int) -> bool:
        return any(user["id"] == user_id for user in self.users)
    
    def get_user(self, user_id: int) -> Optional[dict]:
        for user in self.users:
            if user["id"] == user_id:
                return user
            
        return None

    # ====================
    # Cards methods
    # ====================

    def get_cards_count(self) -> int:
        return len(self.cards)

    def get_card_by_name(self, name: str) -> Optional[dict]:
        return self.card_map.get(name)
    
    def get_all_cards(self) -> list:
        return self.cards
    
    def get_cards_by_bundle(self, bundle_name: str) -> Optional[list[dict]]:
        if bundle_name not in self.bundle_cache:
            return []

        cards = []
        for card in self.cards:
            if card["bundle"] == bundle_name:
                cards.append(card)

        return cards

    def get_cards_by_collection(self, collection_name: str) -> Optional[list[dict]]:
        if collection_name not in self.collection_cache:
            return []

        cards = []
        for card in self.cards:
            if card["collection"] == collection_name:
                cards.append(card)

        return cards
    
    def get_cards_by_rarity(self, rarity: str) -> Optional[list[dict]]:
        cards = []
        for card in self.cards:
            if card["rarity"] == rarity:
                cards.append(card)

        return cards
    
    def get_cards_by_tag(self, tag: str) -> Optional[list]:
        if tag not in self.tag_cache:
            return []
        
        cards = []
        for card in self.cards:
            if tag in card["tags"]:
                cards.append(card)

        return cards

    def get_cards_from_list(self, card_list: list) -> list[dict]:
        cards = []
        for card_name in card_list:
            card = self.get_card_by_name(card_name)
            if card is not None:
                cards.append(card)

        return cards
    
    def get_cards_by_traits(self, bundle: Optional[str] = None, collection: Optional[str] = None, rarity: Optional[str] = None, tag: Optional[str] = None):
        bundle_cards = []
        collection_cards = []
        rarity_cards = []
        tags_cards = []

        if bundle:
            bundle_cards = self.get_cards_by_bundle(bundle)

        if collection:
            collection_cards = self.get_cards_by_collection(collection)

        if rarity:
            rarity_cards = self.get_cards_by_rarity(rarity)

        if tag:
            tags_cards = self.get_cards_by_tag(tag)
        # if tags:
        #     for tag in tags:
        #         tagged_cards = self.get_cards_by_tag(tag)
        #         if tagged_cards:
        #             tags_cards = tags_cards + tagged_cards


        lists = [lst for lst in [bundle_cards, collection_cards, rarity_cards, tags_cards] if lst]
        
        if len(lists) == 1:
            return lists[0]
        
        if not lists:
            return []
        
        maps = [
            {item["name"]: item for item in lst}
            for lst in lists
        ]

        name_sets = [set(m.keys()) for m in maps]

        common_names = set.intersection(*name_sets)

        base_map = maps[0]

        return [base_map[name] for name in common_names]

    # ====================
    # Packs methods
    # ====================

    def get_pack_by_name(self, name: str) -> Optional[dict]:
        for pack in self.packs:
            if pack["name"] == name:
                return pack
            
        return None
