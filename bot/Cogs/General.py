import random

import discord
from discord.ext import commands

# Data
from bot.Data.Card import Card
from bot.Data.Pack import Pack
from bot.Data.User import User

# Views
from bot.Views.PageView import PageView

# Utils
from bot.Utils.Enums import RARITY_WEIGHT

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="test", description="A test command")
    async def test(self, interaction:discord.Interaction):
        cards = self.bot.datadriver.get_all_cards()
        pages = [card.to_container() for card in cards]
        view = PageView(pages, interaction.user.id, "All cards")
        await interaction.response.send_message(view=view)

    @discord.app_commands.command(name="lesgo", description="A test command")
    async def lesgo(self, interaction:discord.Interaction):
        if self.bot.datadriver.user_exist(interaction.user.id):
            await interaction.response.send_message("User already exist.")
            return
        
        self.bot.datadriver.create_user(user_id=interaction.user.id)
        await interaction.response.send_message("Your profile has been created.")

    @discord.app_commands.command(name="profile", description="A test command")
    async def profile(self, interaction:discord.Interaction):
        pass

    @discord.app_commands.command(name="open", description="Open a pack")
    async def open_pack(self, interaction:discord.Interaction, pack_name:str):
        pack = self.bot.datadriver.get_pack_by_name(pack_name)
        if pack is None:
            await interaction.response.send_message("Pack not found")
            return

        card_names = pack.card_names
        cards = self.bot.datadriver.get_cards_from_list(card_names)

        weights = [RARITY_WEIGHT[c.rarity] for c in cards]
        cards = random.choices(cards, weights=weights, k=5)

        pages = [card.to_container() for card in cards]
        view = PageView(pages, interaction.user.id, f"You've opened {pack.name}")
        await interaction.response.send_message(view=view)

async def setup(bot):
    await bot.add_cog(General(bot))