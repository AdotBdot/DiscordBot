from collections import Counter
import random
from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands

from bot.Views.PageView import PageView
from bot.Views.ShopView import ShopView

from bot.Utils.Autocomplete import ac
from bot.Utils.DataDriver import DataDriver
from bot.Utils.Enums import RARITY_VALUE
from bot.Utils.Helpers import confirm

class Shop(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver = datadriver

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
    @app_commands.autocomplete(card=ac("user_card"))
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
    @app_commands.autocomplete(card=ac("user_card"))
    async def sell_duplicates(self, interaction: discord.Interaction, card: str):
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return

        if not self.datadriver.card_exist(card):
            await interaction.response.send_message(content=f"Card not found.")
            return
        
        card_data = self.datadriver.get_card_by_name(card)
        locked_rarities = self.datadriver.get_user_locked_rarities(user_id)
        locked_collections = self.datadriver.get_user_locked_collections(user_id)

        if card_data["rarity"] in locked_rarities or card_data["collection"] in locked_collections: # type: ignore
            await interaction.response.send_message(content=f"**{card}** is protected and cannot be sold.")
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
        
        # Process locked cards
        locked_rarities = self.datadriver.get_user_locked_rarities(user_id)
        locked_collections = self.datadriver.get_user_locked_collections(user_id)

        cards_df = self.datadriver.cards.loc[list(duplicates.keys())]
        cards_df = cards_df[~cards_df["rarity"].isin(locked_rarities) & ~cards_df["collection"].isin(locked_collections)]

        duplicates = {card: duplicates[card] for card in cards_df.index}

        if not duplicates:
            await interaction.followup.send(content="You don't have any duplicates to sell.")
            return

        # Count cards and value
        total_value = 0
        total_cards = 0

        for row in cards_df.itertuples():
            amount = duplicates[row.Index]

            total_cards += amount
            total_value += RARITY_VALUE[row.rarity] * amount # type: ignore

        # Confirm sale
        confirmed = await confirm(
            self.bot,
            interaction,
            f"You are about to sell **{total_cards}** cards for **{total_value}** 🥥. Are you sure?"
        )

        if not confirmed:
            await interaction.followup.send(content="Sale cancelled.")
            return
        
        # Build new inventory
        remaining_to_sell = Counter(duplicates)
        new_intentory = []
        
        for card in user_cards:
            if remaining_to_sell[card] > 0:
                remaining_to_sell[card] -= 1
            else:
                new_intentory.append(card)

        self.datadriver.set_user_cards(user_id, new_intentory)

        # Give cocoses to user
        user_cash = self.datadriver.get_user_cash(user_id)
        self.datadriver.set_user_cash(user_id, user_cash + total_value)

        await interaction.followup.send(
            content=(
                f"Successfully sold **{total_cards} duplicate cards**.\n"
                f"You received **{total_value:,} 🥥**."
            )
        )

    # ====================
    # Daily commands
    # ====================

    @app_commands.command(name="daily", description="Retrieve daily rewards.")
    async def daily(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message("Slow down. You don't have your profile yet. Use **/help** for more information.")
            return

        if self.datadriver.user_claimed_daily(user_id):
            await interaction.response.send_message("You've already claimed your dialy rewards.")
            return
        
        self.datadriver.cache["daily_claims"].append(user_id)

        reward_cash = random.randint(100, 200)
        reward_pack = random.choice(self.datadriver.packs_cache)

        user_cash = self.datadriver.get_user_cash(user_id)
        user_packs = self.datadriver.get_user_packs(user_id)

        self.datadriver.set_user_cash(user_id, user_cash + reward_cash)
        self.datadriver.set_user_packs(user_id, user_packs.append(reward_pack)) # type: ignore

        await interaction.response.send_message(content=f"You've received **{reward_pack}** + {reward_cash} 🥥")
        
# Setup Cog
async def setup(bot):
    await bot.add_cog(Shop(bot, bot.datadriver))