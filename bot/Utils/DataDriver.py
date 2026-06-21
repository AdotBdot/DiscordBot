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

        self.cards_df = pd.DataFrame(columns=["rarity", "bundle", "collection", "tags"]).set_index(pd.Index([], name="name"))
        self.packs_df = pd.DataFrame(columns=["cards"]).set_index(pd.Index([], name="name"))
        self.users_df = pd.DataFrame(columns=["cards", "packs", "cash", "melons"]).set_index(pd.Index([], name="id"))

    def initialize_database(self):
        self.logger.info("Initializing database...")

        self.load_cards()
        self.load_packs()
        self.load_users()

        self.init_card_caches()

    def init_card_caches(self):
        self.bundle_cache = sorted(self.cards_df["bundle"].dropna().unique().tolist())
        self.collection_cache = sorted(self.cards_df["collection"].dropna().unique().tolist())
        self.packs_cache = sorted(self.packs_df.index.unique().tolist())

        self.tags_cache = sorted({
            tag
            for tags in self.cards_df["tags"].dropna()
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

        self.cards_df = pd.DataFrame(cards).set_index("name")
        self.logger.info(f"Loaded {len(self.cards_df)} card(s)")

    def load_packs(self):
        all_cards = set(self.cards_df.index)
        bundles = self.cards_df.groupby("bundle").apply(lambda df: df.index.to_list()).to_dict() if "bundle" in self.cards_df.columns else {}
        collections = self.cards_df.groupby("collection").apply(lambda df: df.index.to_list()).to_dict() if "collection" in self.cards_df.columns else {}

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

        self.packs_df = pd.DataFrame(packs).set_index("name")
        self.logger.info(f"Loaded {len(self.packs_df)} pack(s)")
    
    def load_users(self):
        users_data = []

        for file in Path("data/users").glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                users_data.append(json.load(f))

        if users_data:
            self.users_df = pd.DataFrame(users_data).set_index("id")
        else:
            self.users_df = pd.DataFrame(columns=["cards", "packs", "cash", "melons", "upgrades"]).set_index(pd.Index([], name="id"))

        self.logger.info(f"Loaded {len(self.users_df)} user(s)")

    def load_config(self) -> dict:
        return {}

    # ====================
    # User methods
    # ====================

    def user_exist(self, user_id: int):
        return user_id in self.users_df.index

    def create_user(self, user_id: int):
        if self.user_exist(user_id):
            raise ValueError(f"User {user_id} already exists")
        
        user_data = {
            "cards": [],
            "packs": ["Common Pack"],
            "upgrades": {
                "luck": 1
            },
            "cash": 0,
            "melons": 0
        }

        self.users_df.loc[user_id] = user_data

        self.save_user(user_id)

        self.logger.info(f"Created user {user_id} and saved to database")

    def get_user(self, user_id: int):
        if not self.user_exist(user_id):
            return None

        return self.users_df.loc[user_id]

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
        
        user_data = self.users_df.loc[user_id].to_dict()
        user_data["id"] = user_id

        file_path = USERS_FOLDER / f"{user_id}.json"
        file_path.write_text(json.dumps(user_data, indent=2, ensure_ascii=False), encoding="utf-8")

        return self.users_df.loc[user_id]

    # ====================
    # Cards methods
    # ====================

    def get_cards_count(self) -> int:
        return len(self.cards_df)

    def get_card_by_name(self, name: str):
        if name not in self.cards_df.index:
            return None
        
        return self.cards_df.loc[name]
    
    def get_all_cards(self) -> pd.DataFrame:
        return self.cards_df.copy()

    def get_cards_by_names(self, names: list[str]) -> pd.DataFrame:
        names_set = set(names)

        existing = names_set.intersection(self.cards_df.index)

        if not existing:
            return pd.DataFrame(columns=self.cards_df.columns)

        return self.cards_df.loc[list(existing)]
    
    def get_cards_by_traits(self, bundle: Optional[str] = None, collection: Optional[str] = None, rarity: Optional[str] = None, tag: Optional[str] = None) -> pd.DataFrame:
        if all(x is None for x in [bundle, collection, rarity, tag]):
            raise ValueError("At least one trait must be provided")  

        df = self.cards_df

        if bundle is not None:
            df = df[df["bundle"] == bundle]
        if collection is not None:
            df = df[df["collection"] == collection]
        if rarity is not None:
            df = df[df["rarity"] == rarity]
        if tag is not None:
            df = df[df["tags"].apply(lambda tags: tag in tags)]

        return df
    
    def get_user_cards(self, user_id: int, bundle: Optional[str] = None, collection: Optional[str] = None, rarity: Optional[str] = None, tag: Optional[str] = None) -> pd.DataFrame:
        if user_id not in self.users_df.index:
            return pd.DataFrame(columns=self.cards_df.columns)
        
        user_cards = self.users_df.at[user_id, "cards"]

        if not user_cards:
            return pd.DataFrame(columns=self.cards_df.columns)
        
        df = self.cards_df.loc[user_cards]

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

    def get_pack_by_name(self, name: str):
        if not name in self.packs_df.index:
            return None

        return self.packs_df.loc[name]
    
    def get_user_packs(self, user_id: int) -> list[str]:
        if not self.user_exist(user_id):
            return []
        
        packs = self.users_df.at[user_id, "packs"]

        if isinstance(packs, list):
            return packs
        
        return []
