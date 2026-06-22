import asyncio
import json
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

CARDS_FOLDER = Path("data/cards")
PACKS_FOLDER = Path("data/packs")
USERS_FOLDER = Path("data/users")

class DataDriverScheduler:
    def __init__(self, datadriver: DataDriver):
        self.datadriver = datadriver
        self._task = None
        self.interval = 60

    async def run(self):
        while True:
            await asyncio.sleep(self.interval)

            dirty = self.datadriver.get_dirty_users()
            if not dirty:
                continue
            
            self.datadriver.clear_dirty_users()

            for user_id in dirty:
                self.datadriver.save_user(user_id)

class DataDriver:
    def __init__(self, logs_handler):
        self.logger = logging.getLogger("DataDriver")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.logger.addHandler(logs_handler)

        self.dirty_users: set[int] = set()
        self.config = {}

        self.bundle_cache: list[str] = []
        self.collection_cache: list[str] = []
        self.tag_cache: list[str] = []
        self.packs_cache: list[str] = []

        self.cards = pd.DataFrame(columns=["rarity", "bundle", "collection", "tags"]).set_index(pd.Index([], name="name"))
        self.packs = pd.DataFrame(columns=["cards"]).set_index(pd.Index([], name="name"))
        self.users = pd.DataFrame(columns=["cards", "packs", "cash", "melons"]).set_index(pd.Index([], name="id"))

    def initialize_database(self):
        self.logger.info("Initializing database...")

        self.load_cards()
        self.load_packs()
        self.load_users()

        self.init_card_caches()

    def init_card_caches(self):
        self.bundle_cache = sorted(self.cards["bundle"].dropna().unique().tolist())
        self.collection_cache = sorted(self.cards["collection"].dropna().unique().tolist())
        self.packs_cache = sorted(self.packs.index.unique().tolist())

        self.tags_cache = sorted({
            tag
            for tags in self.cards["tags"].dropna()
            for tag in tags
        })

    def load_cards(self):
        cards_data = []
        for file in Path("data/cards").glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                cards_data.append(json.load(f))

        cards = []
        for data in cards_data:
            for bundle in data:
                for collection in bundle["collections"]:
                    for card in collection["cards"]:
                        cards.append({
                            "name": card["name"],
                            "bundle": bundle["name"],
                            "collection": collection["name"],
                            "rarity": card["rarity"],
                            "description": card["description"],
                            "image_url": card["image_url"],
                            "tags": card["tags"]
                        })

        self.cards = pd.DataFrame(cards).set_index("name")
        self.logger.info(f"Loaded {len(self.cards)} card(s)")

    def load_packs(self):
        all_cards = set(self.cards.index)
        bundles = self.cards.groupby("bundle").apply(lambda df: df.index.to_list()).to_dict() if "bundle" in self.cards.columns else {}
        collections = self.cards.groupby("collection").apply(lambda df: df.index.to_list()).to_dict() if "collection" in self.cards.columns else {}

        packs = []
        for file in Path("data/packs").glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                file_packs = json.load(f)
        
        for pack in file_packs:
            name = pack["name"]
            ptype = pack["type"]

            if ptype == "all":
                cards = list(all_cards)
            elif ptype == "bundle":
                bundle_name = pack["bundle_name"]
                cards = bundles.get(bundle_name, [])
            elif ptype == "collection":
                collection_name = pack["collection_name"]
                cards = collections.get(collection_name, [])
            elif ptype == "custom":
                cards = [c for c in pack.get("cards", []) if c in all_cards]
            else:
                self.logger.info(f"Invalid pack type '{ptype}' for pack '{name}'. Skipping")
                continue
            
            packs.append({"name": name, "cards": cards})

        self.packs = pd.DataFrame(packs).set_index("name")
        self.logger.info(f"Loaded {len(self.packs)} pack(s)")
    
    def load_users(self):
        users_data = []

        for file in Path("data/users").glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                users_data.append(json.load(f))

        if users_data:
            self.users = pd.DataFrame(users_data).set_index("id")
        else:
            self.users = pd.DataFrame(columns=["cards", "packs", "cash", "melons", "upgrades"]).set_index(pd.Index([], name="id"))

        self.logger.info(f"Loaded {len(self.users)} user(s)")

    def load_config(self) -> dict:
        return {}

    # ====================
    # User methods
    # ====================

    def user_exist(self, user_id: int):
        return user_id in self.users.index

    def create_user(self, user_id: int):
        if self.user_exist(user_id):
            raise ValueError(f"User {user_id} already exists")
        
        user_data = {
            "cards": [],
            "packs": ["Common Pack"],
            "upgrades": {
                "luck": 1,
                "drop_rate": 1,
                "pack_size": 1
            },
            "cash": 0,
            "melons": 0
        }

        self.users.loc[user_id] = user_data

        self.save_user(user_id)

        self.logger.info(f"Created user {user_id} and saved to database")

    def get_user(self, user_id: int):
        if not self.user_exist(user_id):
            return None

        return self.users.loc[user_id]

    def mark_dirty(self, user_id: int):
        self.dirty_users.add(user_id)

    def get_dirty_users(self) -> list[int]:
        return list(self.dirty_users)
    
    def clear_dirty_users(self):
        self.dirty_users.clear()

    def save_user(self, user_id: int):
        if not self.user_exist(user_id):
            self.logger.info(f"User {user_id} doesn't exist in database")
            return
        
        user_data = self.users.loc[user_id].to_dict()
        user_data["id"] = user_id

        file_path = USERS_FOLDER / f"{user_id}.json"
        file_path.write_text(json.dumps(user_data, indent=2, ensure_ascii=False), encoding="utf-8")

        return self.users.loc[user_id]
    
    def get_user_cards(self, user_id: int) -> list[str]:
        return self.users.at[user_id, "cards"] or [] # type: ignore
    
    def set_user_cards(self, user_id: int, cards: list[str]):
        self.users.at[user_id, "cards"] = cards # type: ignore
        self.mark_dirty(user_id)

    def get_user_cash(self, user_id: int) -> int:
        return self.users.at[user_id, "cash"] or 0 # type: ignore
    
    def set_user_cash(self, user_id: int, cash: int):
        self.users.at[user_id, "cash"] = cash
        self.mark_dirty(user_id)
    
    def get_user_melones(self, user_id: int) -> int:
        return self.users.at[user_id, "melons"] or 0 # type: ignore

    def set_user_melones(self, user_id: int, melons: int):
        self.users.at[user_id, "melons"] = melons
        self.mark_dirty(user_id)

    def get_user_packs(self, user_id: int) -> list[str]:
        return self.users.at[user_id, "packs"] or [] # type: ignore

    def set_user_packs(self, user_id: int, packs: list[str]):
        self.users.at[user_id, "packs"] = packs # type: ignore
        self.mark_dirty(user_id)

    def get_user_upgrades(self, user_id: int) -> dict:
        return self.users.at[user_id, "upgrades"] or {} # type: ignore
    
    def set_user_upgrades(self, user_id: int, upgrades: dict):
        self.users.at[user_id, "upgrades"] = upgrades # type: ignore
        self.mark_dirty(user_id)

    # ====================
    # Cards methods
    # ====================

    def card_exist(self, name: str) -> bool:
        return name in self.cards.index

    def get_cards_count(self) -> int:
        return len(self.cards)

    def get_card_by_name(self, name: str):
        if name not in self.cards.index:
            return None
        
        return self.cards.loc[name]
    
    def get_all_cards(self) -> pd.DataFrame:
        return self.cards.copy()

    def get_cards_by_names(self, names: list[str]) -> pd.DataFrame:
        names_set = set(names)

        existing = names_set.intersection(self.cards.index)

        if not existing:
            return pd.DataFrame(columns=self.cards.columns)

        return self.cards.loc[list(existing)]
    
    def get_cards_by_traits(self, user_id: Optional[int] = None, bundle: Optional[str] = None, collection: Optional[str] = None, rarity: Optional[str] = None, tag: Optional[str] = None) -> pd.DataFrame:
        if all(x is None for x in [user_id, bundle, collection, rarity, tag]):
            raise ValueError("At least one trait must be provided")  

        df = self.cards
        if user_id and self.user_exist(user_id):
            user_cards = self.users.at[user_id, "cards"] or []
            
            if not user_cards:
                return pd.DataFrame(columns=self.cards.columns)
            
            df = df.loc[user_cards]

        if bundle is not None:
            df = df[df["bundle"] == bundle]
        if collection is not None:
            df = df[df["collection"] == collection]
        if rarity is not None:
            df = df[df["rarity"] == rarity]
        if tag is not None:
            df = df[df["tags"].apply(lambda tags: tag in tags)]

        return df # type: ignore

    # ====================
    # Packs methods
    # ====================

    def pack_exist(self, name: str) -> bool:
        return name in self.packs.index

    def get_pack_by_name(self, name: str):
        if not name in self.packs.index:
            return None

        return self.packs.loc[name]

    def get_pack_cards(self, name: str) -> list[str]:
        return self.packs.at[name, "cards"] or [] # type: ignore