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

    async def user_card_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if len(current) < 3:
            return[]
        
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            return []
        
        user_cards = self.datadriver.cards_df.at[user_id, "cards"]

        choices = [app_commands.Choice(name=card, value=card) for card in user_cards if current.lower() in card.lower()] # type: ignore

        return choices[:25]

    async def user_pack_autocomplete(self, interaction: discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
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

    # ====================
    # Trade commands
    # ====================

    trade = app_commands.Group(name="trade", description="Trade related commands")

    @trade.command(name="give_card", description="Give card to user.")
    @app_commands.autocomplete(card_name=user_card_autocomplete)
    async def trade_give_card(self, interaction: discord.Interaction, to: discord.Member, card_name: str):
        user_id = interaction.user.id
        target_user_id = to.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return
        elif not self.datadriver.user_exist(target_user_id):
            await interaction.response.send_message(content=f"Slow down. {to.name} don't have his profile yet.")
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
        self.datadriver.mark_dirty(user_id)
        self.datadriver.mark_dirty(target_user_id)

        await interaction.response.send_message(content=f"You gave {card_name} to {to.name}.")

    @trade.command(name="give_pack", description="Give card to user.")
    @app_commands.autocomplete(pack_name=user_pack_autocomplete)
    async def trade_give_pack(self, interaction: discord.Interaction, to: discord.Member, pack_name: str):
        user_id = interaction.user.id
        target_user_id = to.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return
        elif not self.datadriver.user_exist(target_user_id):
            await interaction.response.send_message(content=f"Slow down. {to.name} don't have his profile yet.")
            return

        user_packs = self.datadriver.users_df.at[user_id, "packs"] or []

        if not pack_name in user_packs: # type: ignore
            await interaction.response.send_message(content=f"You don't have {pack_name} in your inventory.")
            return

        # Update users packs
        target_user_packs = self.datadriver.users_df.at[target_user_id, "packs"] or []
        user_packs.remove(pack_name) # type: ignore
        target_user_packs.append(pack_name) # type: ignore

        self.datadriver.users_df.at[user_id, "packs"] = user_packs # type: ignore
        self.datadriver.users_df.at[target_user_id, "packs"] = target_user_packs # type: ignore

        # Save Users
        self.datadriver.mark_dirty(user_id)
        self.datadriver.mark_dirty(target_user_id)

        await interaction.response.send_message(content=f"You gave {pack_name} to {to.name}.")

    @trade.command(name="give_cocoses", description="Give card to user.")
    async def trade_give_cocoses(self, interaction: discord.Interaction, to: discord.Member, cocoses: int):
        user_id = interaction.user.id
        target_user_id = to.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return
        elif not self.datadriver.user_exist(target_user_id):
            await interaction.response.send_message(content=f"Slow down. {to.name} don't have his profile yet.")
            return

        user_cash = self.datadriver.users_df.at[user_id, "cash"] or 0

        if user_cash < cocoses: # type: ignore
            await interaction.response.send_message(content=f"You don't enough cocoses.")
            return

        # Update users
        target_user_cash = self.datadriver.users_df.at[target_user_id, "cash"] or 0

        self.datadriver.users_df.at[user_id, "cash"] = user_cash - cocoses # type: ignore
        self.datadriver.users_df.at[target_user_id, "cash"] = target_user_cash + cocoses # type: ignore

        # Save Users
        self.datadriver.mark_dirty(user_id)
        self.datadriver.mark_dirty(target_user_id)

        await interaction.response.send_message(content=f"You gave {cocoses}🥥 to {to.name}.")

# Setup Cog
async def setup(bot):
    await bot.add_cog(Trade(bot, bot.datadriver))