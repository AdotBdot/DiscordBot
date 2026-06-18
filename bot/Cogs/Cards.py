from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.Utils.Enums import RARITY_WEIGHT, RARITY_EMOJI, RARITY_ORDER
from bot.Utils.DataDriver import DataDriver

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
        
        df = self.datadriver.get_cards_by_traits(bundle=bundle, collection=collection, rarity=rarity, tag=tag)

        if df.empty:
            await interaction.response.send_message("No cards found.")
            return

        if sort_by:
            reversed = "Descending" in sort_by

            if "Rarity" in sort_by:
                df = df.copy()
                df["rarity_rank"] = df["rarity"].map(RARITY_ORDER)
                df = df.sort_values("rarity_rank", ascending=not reversed)
            elif "Name" in sort_by:
                df = df.sort_values("name", ascending=not reversed)
            elif "Collection" in sort_by:
                df = df.sort_values("collection", ascending=not reversed)
            elif "Bundle" in sort_by:
                df = df.sort_values("bundle", ascending=not reversed)
            else:
                await interaction.response.send_message(content=f"Invalid key: {sort_by}")
                return

        pages = []
        for i in range(0, len(df), 20):
            chunk = df.iloc[i:i + 20]
            msg = "\n".join(
                f"**{RARITY_EMOJI[row["rarity"]]} {row["rarity"]}**: {key}" 
                for key, row in chunk.iterrows()
            )

            container = discord.ui.Container()
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
        df = self.datadriver.get_cards_by_traits(bundle=bundle, collection=collection, rarity=rarity, tag=tag)

        if df.empty:
            await interaction.response.send_message("No cards found.")
            return

        if sort_by:
            reversed = "Descending" in sort_by

            if "Rarity" in sort_by:
                df = df.copy()
                df["rarity_rank"] = df["rarity"].map(RARITY_ORDER)
                df = df.sort_values("rarity_rank", ascending=not reversed)
            elif "Name" in sort_by:
                df = df.sort_values("name", ascending=not reversed)
            elif "Collection" in sort_by:
                df = df.sort_values("collection", ascending=not reversed)
            elif "Bundle" in sort_by:
                df = df.sort_values("bundle", ascending=not reversed)
            else:
                await interaction.response.send_message(content=f"Invalid key: {sort_by}")
                return

        pages = [card_to_container(row) for _, row in df.iterrows()]
        view = PageView(pages=pages, author_id=interaction.user.id)
        await interaction.response.send_message(view=view)

# Setup Cog
async def setup(bot):
    await bot.add_cog(Cards(bot, bot.datadriver))