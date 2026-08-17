import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.Utils.Autocomplete import ac
from bot.Utils.DataDriver import DataDriver
from bot.Utils.Enums import BASE_RARITY_WEIGHT, RARITIES, RARITY_EMOJI, RARITY_ORDER

from bot.Views.DataViews import card_to_container
from bot.Views.PageView import PageView

class Cards(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver = datadriver
    
        self.logger = logging.getLogger("Cards")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        if not self.logger.handlers:
            self.logger.addHandler(bot.logs_handler)
            self.logger.addHandler(bot.file_handler)

    # ====================
    # Card commands
    # ====================

    card = app_commands.Group(name="cards", description="Cards related commands.")

    @card.command(name="list", description="Lists cards with selected traits.")
    @app_commands.autocomplete(bundle=ac("bundle"), collection=ac("collection"), rarity=ac("rarity"), tag=ac("tag"), sort_by=ac("sort_by"))
    async def card_list(self, interaction: discord.Interaction, bundle: Optional[str] = None, collection: Optional[str] = None,
                        rarity: Optional[str] = None, tag: Optional[str] = None, sort_by: Optional[str] = None):
        # Query cards
        df = self.datadriver.get_cards_by_traits(bundle=bundle, collection=collection, rarity=rarity, tag=tag)

        if df.empty:
            await interaction.response.send_message("No cards found.")
            return

        # Sort cards
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

        # UI
        pages = []
        for i in range(0, len(df), 20):
            chunk = df.iloc[i:i + 20]
            msg = "\n".join(
                f"{RARITY_EMOJI[row["rarity"]]} {key}" 
                for key, row in chunk.iterrows()
            )

            container = discord.ui.Container()
            container.add_item(discord.ui.TextDisplay(content=msg))
            pages.append(container)

        view = PageView(
            author_id=interaction.user.id,
            pages=pages
        )
        
        await interaction.response.send_message(view=view)

    @card.command(name="gallery", description="Displays cards gallery with selected traits.")
    @app_commands.autocomplete(bundle=ac("bundle"), collection=ac("collection"), rarity=ac("rarity"), tag=ac("tag"), sort_by=ac("sort_by"))
    async def card_gallery(self, interaction: discord.Interaction, bundle: Optional[str] = None, collection: Optional[str] = None, 
                           rarity: Optional[str] = None, tag: Optional[str] = None, sort_by: Optional[str] = None):
        # Query cards
        df = self.datadriver.get_cards_by_traits(bundle=bundle, collection=collection, rarity=rarity, tag=tag)

        if df.empty:
            await interaction.response.send_message("No cards found.")
            return

        # Sort cards
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

        # UI
        pages = [card_to_container(row) for _, row in df.iterrows()]
        view = PageView(
            author_id=interaction.user.id,
            pages=pages
        )

        await interaction.response.send_message(view=view)

    @card.command(name="search", description="Search for a card.")
    async def card_search(self, interaction: discord.Interaction, name: str):
        # Checks
        if len(name) < 3:
            await interaction.response.send_message("Querry must be at least 3 characters long.")
            return
        
        # Query cards
        df = self.datadriver.cards.copy()
        df = df[df.index.str.contains(name, case=False, na=False)]
        
        if df.empty:
            await interaction.response.send_message("No cards found.")
            return

        # UI
        pages = [card_to_container(row) for _, row in df.iterrows()]
        view = PageView(
            author_id=interaction.user.id,
            pages=pages
        )

        await interaction.response.send_message(view=view)

# Setup Cog
async def setup(bot):
    await bot.add_cog(Cards(bot, bot.datadriver))