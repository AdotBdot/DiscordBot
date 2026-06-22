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
        
        user_cards = self.datadriver.get_user_cards(user_id)

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

        user_cards = self.datadriver.get_user_cards(user_id)

        if not card_name in user_cards:
            await interaction.response.send_message(content=f"You don't have {card_name} in your inventory.")
            return

        # Update users cards
        target_user_cards = self.datadriver.get_user_cards(target_user_id)
        user_cards.remove(card_name)
        target_user_cards.append(card_name)

        self.datadriver.set_user_cards(user_id, user_cards)
        self.datadriver.set_user_cards(target_user_id, target_user_cards)

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

        user_packs = self.datadriver.get_user_packs(user_id)

        if not pack_name in user_packs:
            await interaction.response.send_message(content=f"You don't have {pack_name} in your inventory.")
            return

        # Update users packs
        target_user_packs = self.datadriver.get_user_packs(target_user_id)
        user_packs.remove(pack_name)
        target_user_packs.append(pack_name)

        self.datadriver.set_user_packs(user_id, user_packs)
        self.datadriver.set_user_packs(target_user_id, target_user_packs)

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

        user_cash = self.datadriver.get_user_cash(user_id)

        if user_cash < cocoses:
            await interaction.response.send_message(content=f"You don't enough cocoses.")
            return

        # Update users
        target_user_cash = self.datadriver.get_user_cash(target_user_id)

        self.datadriver.set_user_cash(user_id, user_cash - cocoses)
        self.datadriver.set_user_cash(target_user_id, target_user_cash + cocoses)

        # Save Users
        self.datadriver.mark_dirty(user_id)
        self.datadriver.mark_dirty(target_user_id)

        await interaction.response.send_message(content=f"You gave {cocoses}🥥 to {to.name}.")

# Setup Cog
async def setup(bot):
    await bot.add_cog(Trade(bot, bot.datadriver))