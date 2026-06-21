from collections import defaultdict
import random
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.Utils.Enums import BASE_RARITY_WEIGHT
from bot.Utils.DataDriver import DataDriver

from bot.Views.PageView import PageView
from bot.Views.DataViews import card_to_container

class Packs(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver = datadriver

    # ====================
    # Autocomplete
    # ====================

    async def pack_autocomplete(self, interaction: discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
        user_id = interaction.user.id

        if user_id not in self.datadriver.users_df.index:
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
    # Pack commands
    # ====================

    pack = app_commands.Group(name="pack", description="Pack related commands.")

    @pack.command(name="open", description="Opens pack from your inventory.")
    @app_commands.autocomplete(pack_name=pack_autocomplete)
    async def pack_open(self, interaction: discord.Interaction, pack_name: str, count: Optional[int]):
        user_id = interaction.user.id
        
        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message("User does not exist in database.")
            return
        
        if pack_name not in self.datadriver.packs_df.index:
            await interaction.response.send_message("Pack not found.")
            return
        
        open_count = count or 1
        user_packs = self.datadriver.users_df.at[user_id, "packs"] or []
        
        if user_packs.count(pack_name) < open_count: # type: ignore
            await interaction.response.send_message(f"You don't have enough **{pack_name}** in your inventory")
            return

        # Remove pack from user inventory
        for _ in range(open_count):
            user_packs.remove(pack_name) # type: ignore

        self.datadriver.users_df.at[user_id, "packs"] = user_packs  # type: ignore

        # Get cards from pack
        pack_cards = self.datadriver.packs_df.at[pack_name, "cards"]
        cards = self.datadriver.cards_df.loc[pack_cards]

        # Group by rarity
        by_rarity = {rarity: group for rarity, group in cards.groupby("rarity")}

        rarities = list(by_rarity.keys())
        weights = [BASE_RARITY_WEIGHT[r] for r in rarities]  # type: ignore

        # Open pack
        result = []

        for _ in range(5 * open_count):
            chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]
            pool = by_rarity[chosen_rarity]
            result.append(pool.iloc[random.randrange(len(pool))])

        # Add card to user
        user_cards = self.datadriver.users_df.at[user_id, "cards"] or []
        user_cards.extend([card.name for card in result]) # type: ignore
        self.datadriver.users_df.at[user_id, "cards"] = user_cards # type: ignore

        # Save user
        self.datadriver.mark_dirty(user_id)

        pages = [card_to_container(card) for card in result]
        view = PageView(
            pages=pages, 
            author_id=interaction.user.id, 
            header=f"You've opened **{pack_name}**"
            )
        
        await interaction.response.send_message(view=view)

    @pack.command(name="list", description="List all available packs.")
    async def list_packs(self, interaction:discord.Interaction):
        packs = self.datadriver.packs_cache

        names = ", ".join([p for p in packs])

        await interaction.response.send_message(f"Packs: {names}")

async def setup(bot):
    await bot.add_cog(Packs(bot, bot.datadriver))