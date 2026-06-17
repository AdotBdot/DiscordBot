import discord
from discord.ext import commands
from discord import app_commands

from bot.Utils.DataDriver import DataDriver

class Trade(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver = datadriver

    # ====================
    # Autocomplete
    # ====================

    async def card_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        user = self.datadriver.get_user(interaction.user.id)
        if not user:
            return []
        
        cards = user["cards"]
        choices = [app_commands.Choice(name=card, value=card) for card in cards if current.lower() in card.lower()]

        return choices[:25]

    # ====================
    # Trade commands
    # ====================

    trade = app_commands.Group(name="trade", description="Trade related commands")

    @trade.command(name="give", description="Give card to user.")
    @app_commands.autocomplete(card_name=card_autocomplete)
    async def trade_give(self, interaction: discord.Interaction, to: discord.Member, card_name: str):
        user = self.datadriver.get_user(interaction.user.id)
        target_user = self.datadriver.get_user(to.id)

        if not user:
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return
        elif not target_user:
            await interaction.response.send_message(content=f"Slow down. {to.name} don't have his profile yet.")
            return
        elif not any([user, target_user]):
            await interaction.response.send_message(content=f"Slow down. You both haven't haven't created your profiles yet. Use **/help** for more information.")
            return
        
        if not card_name in user["cards"]:
            await interaction.response.send_message(content=f"You don't have {card_name} in your inventory.")

        user["cards"].remove(card_name)
        target_user["cards"].append(card_name)

        await interaction.response.send_message(content=f"You gave {card_name} to {to.name}.")
        
async def setup(bot):
    await bot.add_cog(Trade(bot, bot.datadriver))