import discord
from discord import app_commands
from discord.ext import commands

from bot.Utils.DataDriver import DataDriver

from bot.Views.DataViews import card_to_container, user_to_container, inv_to_container
from bot.Views.SimpleView import SimpleView
from bot.Views.PageView import PageView

class Users(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver: DataDriver = datadriver

    @app_commands.command(name="profile", description="Display user profile.")
    async def profile(self, interaction: discord.Interaction):
        user = self.datadriver.get_user(interaction.user.id)

        if user is None:
            await interaction.response.send_message(f"User does not exist in database.")
            return

        container = user_to_container(user, interaction.user.display_avatar.url, self.datadriver.get_cards_count())
        view = SimpleView(content=container, header=f"{interaction.user.mention}\n## Profile", thumbnail=interaction.user.display_avatar.url)

        await interaction.response.send_message(view=view)

    # Inventory commands
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

    @inventory.command(name="cards", description="Display cards in user inventory")
    async def inventory_cards(self, interaction: discord.Interaction):
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


async def setup(bot):
    await bot.add_cog(Users(bot, bot.datadriver))