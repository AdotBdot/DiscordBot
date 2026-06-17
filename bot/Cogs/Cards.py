from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.Utils.Enums import RARITY_WEIGHT, RARITY_EMOJI
from bot.Utils.DataDriver import DataDriver
from bot.Utils.Helpers import chunk_list, sort_list_by_key

from bot.Views.PageView import PageView
from bot.Views.DataViews import card_to_container

class Cards(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver = datadriver

    # ====================
    # Autocomplete
    # ====================

    async def bundle_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        bundles = self.datadriver.bundle_cache
        choices = [app_commands.Choice(name=bundle, value=bundle) for bundle in bundles if current.lower() in bundle.lower()]
        
        return choices[:25]

    async def collection_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        collections = self.datadriver.collection_cache
        choices = [app_commands.Choice(name=collection, value=collection) for collection in collections if current.lower() in collection.lower()]
        
        return choices[:25]

    async def rarity_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        rarities = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
        choices = [app_commands.Choice(name=rarity, value=rarity) for rarity in rarities if current.lower() in rarity.lower()]
        
        return choices[:25]
    
    async def tag_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        tags = self.datadriver.tag_cache
        choices = [app_commands.Choice(name=tag, value=tag) for tag in tags if current.lower() in tag.lower()]
        
        return choices[:25]
    
    async def sort_by_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        sort_bys = ["RarityAscending", "NameAscending", "CollectionAscending", "BundleAscending", 
                    "RarityDescending", "NameDescending", "CollectionDescending", "BundleDescending"]
        choices = [app_commands.Choice(name=sort_by, value=sort_by) for sort_by in sort_bys if current.lower() in sort_by.lower()]
        
        return choices[:25]

    # ====================
    # Card commands
    # ====================

    card = app_commands.Group(name="cards", description="Cards related commands.")

    @card.command(name="list", description="Lists cards with selected traits.")
    @app_commands.autocomplete(bundle=bundle_autocomplete, collection=collection_autocomplete, rarity=rarity_autocomplete, tag=tag_autocomplete, sort_by=sort_by_autocomplete)
    async def card_list(self, interaction: discord.Interaction, 
                        bundle: Optional[str] = None, 
                        collection: Optional[str] = None,
                        rarity: Optional[str] = None,
                        tag: Optional[str] = None,
                        sort_by: Optional[str] = None
                        ):
        
        cards = self.datadriver.get_cards_by_traits(bundle=bundle, collection=collection, rarity=rarity, tag=tag)

        if sort_by:
            reversed = False
            key = ""
            if "Descending" in sort_by:
                reversed = True

            if "Rarity" in sort_by:
                key = "rarity"
            elif "Name" in sort_by:
                key = "name"
            elif "Collection" in sort_by:
                key = "collection"
            elif "Bundle" in sort_by:
                key = "bundle"
            else:
                await interaction.response.send_message(content=f"Invalid key: {sort_by}")
                return
            
            cards = sort_list_by_key(cards, key, reversed)

        cards_chunks = chunk_list(cards, 20)

        pages = []
        for chunk in cards_chunks:
            container = discord.ui.Container()
            msg = "\n".join(f"**{RARITY_EMOJI[card["rarity"]]} {card["rarity"]}**: {card["name"]}" for card in chunk)
            container.add_item(discord.ui.TextDisplay(content=msg))

            pages.append(container)

        view = PageView(pages=pages, author_id=interaction.user.id)
        await interaction.response.send_message(view=view)

    @card.command(name="gallery", description="Lists cards with selected traits.")
    @app_commands.autocomplete(bundle=bundle_autocomplete, collection=collection_autocomplete, rarity=rarity_autocomplete, tag=tag_autocomplete, sort_by=sort_by_autocomplete)
    async def card_gallery(self, interaction: discord.Interaction, 
                        bundle: Optional[str] = None, 
                        collection: Optional[str] = None,
                        rarity: Optional[str] = None,
                        tag: Optional[str] = None,
                        sort_by: Optional[str] = None
                        ):
        cards = self.datadriver.get_cards_by_traits(bundle=bundle, collection=collection, rarity=rarity, tag=tag)

        if sort_by:
            reversed = False
            key = ""
            if "Descending" in sort_by:
                reversed = True

            if "Rarity" in sort_by:
                key = "rarity"
            elif "Name" in sort_by:
                key = "name"
            elif "Collection" in sort_by:
                key = "collection"
            elif "Bundle" in sort_by:
                key = "bundle"
            else:
                await interaction.response.send_message(content=f"Invalid key: {sort_by}")
                return
            
            cards = sort_list_by_key(cards, key, reversed)

        pages = [card_to_container(card) for card in cards]
        view = PageView(pages=pages, author_id=interaction.user.id)
        await interaction.response.send_message(view=view)
async def setup(bot):
    await bot.add_cog(Cards(bot, bot.datadriver))