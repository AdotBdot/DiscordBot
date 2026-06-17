import random

import discord
from discord.ext import commands
from discord import app_commands

# Views
from bot.Views.PageView import PageView

# Utils
from bot.Utils.Enums import RARITY_WEIGHT
from bot.Utils.DataDriver import DataDriver

class General(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver = datadriver

    @app_commands.command(name="lesgo", description="Creates user profile")
    async def lesgo(self, interaction:discord.Interaction):
        if self.datadriver.user_exist(interaction.user.id):
            await interaction.response.send_message("User already exist.")
            return
        
        self.datadriver.create_user(user_id=interaction.user.id)
        await interaction.response.send_message("Your profile has been created.")

    @app_commands.command(name="help", description="Displays help.")
    async def help(self, interaction: discord.Interaction):
        pass

async def setup(bot):
    await bot.add_cog(General(bot, bot.datadriver))