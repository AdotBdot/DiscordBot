from collections import Counter

import discord
from discord.ext import commands
from discord import app_commands

from bot.Utils.Autocomplete import ac
from bot.Utils.DataDriver import DataDriver
from bot.Utils.Helpers import merge_cards

from bot.Views.DataViews import card_to_container
from bot.Views.SimpleView import SimpleView

class Trade(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver = datadriver

    # ====================
    # Trade commands
    # ====================

    trade = app_commands.Group(name="trade", description="Trade related commands")

    @trade.command(name="give_card", description="Give card to user.")
    @app_commands.autocomplete(card=ac("user_card"))
    async def trade_give_card(self, interaction: discord.Interaction, to: discord.Member, card: str):
        user_id = interaction.user.id
        target_user_id = to.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return
        elif not self.datadriver.user_exist(target_user_id):
            await interaction.response.send_message(content=f"Slow down. {to.name} don't have his profile yet.")
            return

        user_cards = self.datadriver.get_user_cards(user_id)

        if not card in user_cards:
            await interaction.response.send_message(content=f"You don't have {card} in your inventory.")
            return

        # Update users cards
        target_user_cards = self.datadriver.get_user_cards(target_user_id)
        user_cards.remove(card)
        target_user_cards.append(card)

        self.datadriver.set_user_cards(user_id, user_cards)
        self.datadriver.set_user_cards(target_user_id, target_user_cards)

        # Save Users
        self.datadriver.mark_dirty(user_id)
        self.datadriver.mark_dirty(target_user_id)

        await interaction.response.send_message(content=f"You gave {card} to {to.name}.")

    @trade.command(name="give_pack", description="Give card to user.")
    @app_commands.autocomplete(pack=ac("user_pack"))
    async def trade_give_pack(self, interaction: discord.Interaction, to: discord.Member, pack: str):
        user_id = interaction.user.id
        target_user_id = to.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return
        elif not self.datadriver.user_exist(target_user_id):
            await interaction.response.send_message(content=f"Slow down. {to.name} don't have his profile yet.")
            return

        user_packs = self.datadriver.get_user_packs(user_id)

        if not pack in user_packs:
            await interaction.response.send_message(content=f"You don't have {pack} in your inventory.")
            return

        # Update users packs
        target_user_packs = self.datadriver.get_user_packs(target_user_id)
        user_packs.remove(pack)
        target_user_packs.append(pack)

        self.datadriver.set_user_packs(user_id, user_packs)
        self.datadriver.set_user_packs(target_user_id, target_user_packs)

        # Save Users
        self.datadriver.mark_dirty(user_id)
        self.datadriver.mark_dirty(target_user_id)

        await interaction.response.send_message(content=f"You gave {pack} to {to.name}.")

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

    @app_commands.command(name="merge", description="Merge cards to get a better one.")
    @app_commands.autocomplete(card1=ac("user_card"), card2=ac("user_card"), card3=ac("user_card"))
    async def merge(self, interaction: discord.Interaction, card1: str, card2: str, card3: str):
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return
        
        selected = [card1, card2, card3]

        # Inventory check
        user_cards = self.datadriver.get_user_cards(user_id)

        invCounter = Counter(user_cards)
        selCounter = Counter(selected)

        has_cards = all(invCounter[name] >= amount for name, amount in selCounter.items())

        if not has_cards:
            await interaction.response.send_message(content=f"You don't have selected cards in your inventory.")
            return
        
        selected_cards = self.datadriver.get_cards_by_names(selected)

        if not selected_cards[0]["rarity"] == selected_cards[1]["rarity"] and selected_cards[1]["rarity"] == selected_cards[2]["rarity"]:
            await interaction.response.send_message(content=f"Selected cards must be the same rarity.")
            return
        
        result = merge_cards(self.datadriver, user_id, selected)

        if result is None:
            await interaction.response.send_message("No possible card found.")
            return
        
        # Update user inventory
        user_cards = self.datadriver.get_user_cards(user_id)
        user_cards.remove(card1)
        user_cards.remove(card2)
        user_cards.remove(card3)
        user_cards.append(result.name) # type: ignore

        self.datadriver.set_user_cards(user_id, user_cards)

        # UI
        container = card_to_container(result)
        view = SimpleView(
            author_id=user_id,
            content=container,
            header="## Merge\nYou have received in merge:"
        )

        await interaction.response.send_message(view=view)


# Setup Cog
async def setup(bot):
    await bot.add_cog(Trade(bot, bot.datadriver))