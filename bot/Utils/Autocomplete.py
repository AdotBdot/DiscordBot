from typing import Callable, Awaitable

import discord
from discord import app_commands

from bot.Utils.DataDriver import DataDriver
from bot.Utils.Enums import RARITIES

AutocompleteFunc = Callable[
    [discord.Interaction, str],
    Awaitable[list[app_commands.Choice[str]]]
]

class AutocompleteService:
    def __init__(self, datadriver: DataDriver):
        self.datadriver: DataDriver = datadriver
        self._registry: dict[str, AutocompleteFunc] = {}

        self._register_all()

    # ----------------------------
    # REGISTRY CORE
    # ----------------------------

    def register(self, name: str, func: AutocompleteFunc):
        self._registry[name] = func

    def _register_all(self):
        self.register("card", self.card)
        self.register("pack", self.pack)
        self.register("bundle", self.bundle)
        self.register("collection", self.collection)
        self.register("tag", self.tag)
        self.register("rarity", self.rarity)
        self.register("sort_by", self.sort_by)
        self.register("user_pack", self.user_pack)
        self.register("user_card", self.user_card)

    def get(self, name: str) -> AutocompleteFunc:
        return self._registry[name]

    # ----------------------------
    # AUTOCOMPLETE FUNCTIONS
    # ----------------------------

    async def bundle(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        bundles = self.datadriver.bundle_cache
        choices = [app_commands.Choice(name=bundle, value=bundle) for bundle in bundles if current.lower() in bundle.lower()]
        
        return choices[:25]

    async def collection(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        collections = self.datadriver.collection_cache
        choices = [app_commands.Choice(name=collection, value=collection) for collection in collections if current.lower() in collection.lower()]
        
        return choices[:25]

    async def rarity(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        rarities = RARITIES
        choices = [app_commands.Choice(name=rarity, value=rarity) for rarity in rarities if current.lower() in rarity.lower()]
        
        return choices[:25]

    async def tag(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        tags = self.datadriver.tag_cache
        choices = [app_commands.Choice(name=tag, value=tag) for tag in tags if current.lower() in tag.lower()]
        
        return choices[:25]

    async def sort_by(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        sort_bys = ["RarityAscending", "NameAscending", "CollectionAscending", "BundleAscending", 
                    "RarityDescending", "NameDescending", "CollectionDescending", "BundleDescending"]
        choices = [app_commands.Choice(name=sort_by, value=sort_by) for sort_by in sort_bys if current.lower() in sort_by.lower()]
        
        return choices[:25]
    
    async def user_card(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if len(current) < 3:
            return []
        
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            return []
        
        user_cards = set(self.datadriver.get_user_cards(user_id))

        choices = [app_commands.Choice(name=card, value=card) for card in user_cards if current.lower() in card.lower()] # type: ignore

        return choices[:25]
    
    async def user_pack(self, interaction: discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            return []
        
        user_packs = self.datadriver.get_user_packs(user_id)

        if not user_packs:
            return []
        
        choices = [
            app_commands.Choice(name=pack, value=pack) 
            for pack in set(user_packs) 
            if current.lower() in pack.lower()
            ]

        return choices[:25]
    
    async def card(self, interaction: discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
        if len(current) < 3:
            return []
        
        df = self.datadriver.cards

        matches = df.index[df.index.str.contains(current, case=False, na=False)]

        return [
            app_commands.Choice(name=name, value=name)
            for name in matches[:25]
        ]

    async def pack(self, interaction: discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
        packs = self.datadriver.packs_cache
        choices = [app_commands.Choice(name=pack, value=pack) for pack in packs if current.lower() in pack.lower()]
        
        return choices[:25]

    # ----------------------------
    # DECORATOR
    # ----------------------------

def ac(name: str):
    async def wrapper(interaction, current):
        return await interaction.client.autocomplete.get(name)(
            interaction,
            current
        )
    return wrapper