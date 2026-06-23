from collections import Counter
from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands

from bot.Views.PageView import PageView
from bot.Views.ShopView import ShopView

from bot.Utils.DataDriver import DataDriver
from bot.Utils.Enums import RARITY_VALUE
from bot.Utils.Helpers import confirm

class Shop(commands.Cog):
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
        
        user_cards = set(self.datadriver.get_user_cards(user_id))

        choices = [app_commands.Choice(name=card, value=card) for card in user_cards if current.lower() in card.lower()] # type: ignore

        return choices[:25]

    # ====================
    # General commands
    # ====================

    @app_commands.command(name="shop")
    async def shop(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return
        
        view = ShopView(user_id, self.datadriver)
        await interaction.response.send_message(view=view)

    # ====================
    # Sell commands
    # ====================

    sell = app_commands.Group(name="sell", description="Sell related commands.")

    @sell.command(name="card")
    @app_commands.autocomplete(card=user_card_autocomplete)
    async def sell_card(self, interaction: discord.Interaction, card: str, amount: Optional[int] = 1):
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return

        if not self.datadriver.card_exist(card):
            await interaction.response.send_message(content=f"Card not found.")
            return

        user_cards = self.datadriver.get_user_cards(user_id)
        inv_counter = Counter(user_cards)
        sell_count = amount or 1

        if inv_counter[card] < sell_count:
            await interaction.response.send_message(content=f"You don't have enough **{card}** in your inventory.")
            return

        # Remove cards from user inventory
        for _ in range(sell_count):
            user_cards.remove(card)

        self.datadriver.set_user_cards(user_id, user_cards)

        # Give cash to user
        rarity = self.datadriver.get_card_by_name(card)["rarity"] # type: ignore
        sell_price = RARITY_VALUE[rarity] * sell_count # type: ignore
        user_cash = self.datadriver.get_user_cash(user_id)

        self.datadriver.set_user_cash(user_id, user_cash + sell_price)

        await interaction.response.send_message(content=f"Sold **{sell_count}x {card}**\nYou received **{sell_price}** 🥥.")

    @sell.command(name="duplicates")
    @app_commands.autocomplete(card=user_card_autocomplete)
    async def sell_duplicates(self, interaction: discord.Interaction, card: str):
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return

        if not self.datadriver.card_exist(card):
            await interaction.response.send_message(content=f"Card not found.")
            return
        
        user_cards = self.datadriver.get_user_cards(user_id)

        amount = user_cards.count(card)

        if amount <= 1:
            await interaction.response.send_message(content=f"You don't have any duplicates of **{card}**.")
            return
        
        # Remove user cards
        for _ in range(amount - 1):
            user_cards.remove(card)

        self.datadriver.set_user_cards(user_id, user_cards)

        # Give cocoses to user
        user_cash = self.datadriver.get_user_cash(user_id)
        rarity = self.datadriver.get_card_by_name(card)["rarity"] # type: ignore
        sell_value = RARITY_VALUE[rarity] * (amount - 1) # type: ignore
        
        self.datadriver.set_user_cash(user_id, user_cash + sell_value)

        await interaction.response.send_message(
            content=(
                f"Sold **{amount - 1}x {card}** duplicates.\n"
                f"You received **{sell_value} 🥥**."
            )
        )

    @sell.command(name="all_duplicates")
    async def sell_all_duplicates(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return

        await interaction.response.defer()

        user_cards = self.datadriver.get_user_cards(user_id)

        if not user_cards:
            await interaction.response.send_message(content=f"You don't have any cards in your collection.")
            return
        
        card_counts = Counter(user_cards)

        duplicates = {card: count - 1 for card, count in card_counts.items() if count > 1}

        if not duplicates:
            await interaction.followup.send(content="You don't have any duplicates to sell.")
            return
        
        # Count cards and value
        cards_df = self.datadriver.get_cards_by_names(list(duplicates.keys()))

        total_value = 0
        total_cards = 0

        for _, row in cards_df.iterrows():
            card_name = row.name
            rarity = row["rarity"]

            amount = duplicates[card_name] # type: ignore

            total_cards += amount
            total_value += RARITY_VALUE[rarity] * amount

        # Confirm sale
        confirmed = await confirm(
            self.bot,
            interaction,
            f"You are about to sell **{total_cards}** cards.\n for **{total_value}** 🥥. Are you sure?"
        )

        if not confirmed:
            await interaction.followup.send(content="Sale cancelled.")
            return
        
        # Remove duplicates
        new_intentory = list(set(user_cards))
        self.datadriver.set_user_cards(user_id, new_intentory)

        # Give cocoses to user
        user_cash = self.datadriver.get_user_cash(user_id)
        self.datadriver.set_user_cash(user_id, user_cash + total_value)
        

        await interaction.followup.send(
            content=(
                f"Successfully sold **{total_cards} duplicate cards**.\n"
                f"You received **{total_value:,} coins**."
            )
        )

# Setup Cog
async def setup(bot):
    await bot.add_cog(Shop(bot, bot.datadriver))