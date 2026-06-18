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
        user_id = interaction.user.id

        user = self.datadriver.get_user(user_id)
        if user is None:
            return []
        
        user_cards = self.datadriver.cards_df.at[user_id, "cards"]

        choices = [app_commands.Choice(name=card, value=card) for card in user_cards if current.lower() in card.lower()] # type: ignore

        return choices[:25]

    # ====================
    # Trade commands
    # ====================

    trade = app_commands.Group(name="trade", description="Trade related commands")

    @trade.command(name="give_card", description="Give card to user.")
    @app_commands.autocomplete(card_name=card_autocomplete)
    async def trade_give_card(self, interaction: discord.Interaction, to: discord.Member, card_name: str):
        user_id = interaction.user.id
        target_user_id = to.id

        user = self.datadriver.get_user(user_id)
        target_user = self.datadriver.get_user(target_user_id)
        if user is None:
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return
        elif target_user is None:
            await interaction.response.send_message(content=f"Slow down. {to.name} don't have his profile yet.")
            return
        elif not any([user, target_user]):
            await interaction.response.send_message(content=f"Slow down. You both haven't haven't created your profiles yet. Use **/help** for more information.")
            return

        user_cards = self.datadriver.users_df.at[user_id, "cards"] or []

        if not card_name in user_cards: # type: ignore
            await interaction.response.send_message(content=f"You don't have {card_name} in your inventory.")
            return

        # Update users cards
        target_user_cards = self.datadriver.users_df.at[target_user_id, "cards"] or []
        user_cards.remove(card_name) # type: ignore
        target_user_cards.append(card_name) # type: ignore

        self.datadriver.users_df.at[user_id, "cards"] = user_cards # type: ignore
        self.datadriver.users_df.at[target_user_id, "cards"] = target_user_cards # type: ignore

        # Save Users
        self.datadriver.save_user(user_id)
        self.datadriver.save_user(target_user_id)

        await interaction.response.send_message(content=f"You gave {card_name} to {to.name}.")

# Setup Cog
async def setup(bot):
    await bot.add_cog(Trade(bot, bot.datadriver))