from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.Utils.DataDriver import DataDriver
from bot.Utils.Enums import RARITY_EMOJI
from bot.Utils.Helpers import chunk_dict

from bot.Views.DataViews import card_to_container, user_to_container, inv_to_container
from bot.Views.SimpleView import SimpleView
from bot.Views.PageView import PageView

class Users(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver: DataDriver = datadriver

    # ====================
    # Autocomplete
    # ====================

    async def bundle_autocomplete(self, interaction: discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
        bundles = self.datadriver.bundle_cache
        choices = [app_commands.Choice(name=bundle, value=bundle) for bundle in bundles if current.lower() in bundle.lower()]
        
        return choices[:25]

    async def collection_autocomplete(self, interaction: discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
        collections = self.datadriver.bundle_cache
        choices = [app_commands.Choice(name=collection, value=collection) for collection in collections if current.lower() in collection.lower()]
        
        return choices[:25]

    async def rarity_autocomplete(self, interaction: discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
        rarities = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
        choices = [app_commands.Choice(name=rarity, value=rarity) for rarity in rarities if current.lower() in rarity.lower()]
        
        return choices[:25]
    
    async def tag_autocomplete(self, interaction: discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
        tags = self.datadriver.tag_cache
        choices = [app_commands.Choice(name=tag, value=tag) for tag in tags if current.lower() in tag.lower()]
        
        return choices[:25]

    # ====================
    # Profile commands
    # ====================

    @app_commands.command(name="profile", description="Display user profile.")
    async def profile(self, interaction: discord.Interaction):
        user = self.datadriver.get_user(interaction.user.id)

        if user is None:
            await interaction.response.send_message(f"User does not exist in database.")
            return

        container = user_to_container(user, self.datadriver.get_cards_count())
        view = SimpleView(content=container, header=f"{interaction.user.mention}\n## Profile", thumbnail=interaction.user.display_avatar.url)

        await interaction.response.send_message(view=view)

    # ====================
    # Inventory commands
    # ====================

    inventory = app_commands.Group(name="inventory", description="Inventory related commands.")

    @inventory.command(name="packs", description="Displays packs in users inventory.")
    async def inventory_packs(self, interaction: discord.Interaction):
        user = self.datadriver.get_user(interaction.user.id)

        if user is None:
            await interaction.response.send_message("User does not exist in database.")
            return
        
        if user["packs"] == []:
            await interaction.response.send_message("You don't have any packs in your inventory.")
            return      

        container = inv_to_container(user, interaction.user.display_avatar.url)
        view = SimpleView(container, header=f"{interaction.user.mention}\n## Inventory", thumbnail=interaction.user.display_avatar.url)

        await interaction.response.send_message(view=view)

    @inventory.command(name="cards_gallery", description="Display cards in user inventory")
    @app_commands.autocomplete(bundle=bundle_autocomplete, collection=collection_autocomplete, rarity=rarity_autocomplete, tag=tag_autocomplete)
    async def inventory_cards_gallery(self, interaction: discord.Interaction, 
                        bundle: Optional[str] = None, 
                        collection: Optional[str] = None,
                        rarity: Optional[str] = None,
                        tag: Optional[str] = None
                        ):
        user = self.datadriver.get_user(interaction.user.id)

        if user is None:
            await interaction.response.send_message("User does not exist in database.")
            return
        
        if user["cards"] == []:
            await interaction.response.send_message("You don't have any cards in your inventory.")
            return           

        cards = {}
        for card in user["cards"]:
            cards[card] = cards.get(card, 0) + 1

        pages = []
        for key, value in cards.items():
            card = self.datadriver.get_card_by_name(key)
            if card:
                page = card_to_container(card)
                page.add_item(discord.ui.TextDisplay(content=f"**{value}x**"))
                pages.append(page)
        
        view = PageView(pages, interaction.user.id, f"{interaction.user.mention}\n## Collection", thumbnail=interaction.user.display_avatar.url)
        await interaction.response.send_message(view=view)

    @inventory.command(name="cards_list", description="Display cards in user inventory")
    @app_commands.autocomplete(bundle=bundle_autocomplete, collection=collection_autocomplete, rarity=rarity_autocomplete, tag=tag_autocomplete)
    async def inventory_cards_list(self, interaction: discord.Interaction, 
                        bundle: Optional[str] = None, 
                        collection: Optional[str] = None,
                        rarity: Optional[str] = None,
                        tag: Optional[str] = None
                        ):
        user = self.datadriver.get_user(interaction.user.id)

        if user is None:
            await interaction.response.send_message("User does not exist in database.")
            return
        
        if user["cards"] == []:
            await interaction.response.send_message("You don't have any cards in your inventory.")
            return           
        
        cards = {}
        for card in user["cards"]:
            cards[card] = cards.get(card, 0) + 1

        cards_chunks = chunk_dict(cards, 20)

        pages = []
        for chunk in cards_chunks:
            container = discord.ui.Container()
            msg = ""
            for key, value in chunk.items():
                card = self.datadriver.get_card_by_name(key)
                if card:
                    entry = f"**{RARITY_EMOJI[card["rarity"]]} {card["rarity"]}**: {card["name"]} **{value}x**\n"
                    msg = msg + entry
            container.add_item(discord.ui.TextDisplay(content=msg))
            pages.append(container)
        
        view = PageView(pages, interaction.user.id, f"{interaction.user.mention}\n## Collection", thumbnail=interaction.user.display_avatar.url)
        await interaction.response.send_message(view=view) 

async def setup(bot):
    await bot.add_cog(Users(bot, bot.datadriver))