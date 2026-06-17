from collections import defaultdict
import random
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.Utils.Enums import RARITY_WEIGHT
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
        user = self.datadriver.get_user(interaction.user.id)

        if not user:
            return []

        choices = [app_commands.Choice(name=pack, value=pack) for pack in set(user["packs"]) if current.lower() in pack.lower()]

        return choices[:25]

    # ====================
    # Pack commands
    # ====================

    pack = app_commands.Group(name="pack", description="Pack related commands.")

    @pack.command(name="open", description="Open pack from your inventory.")
    @app_commands.autocomplete(pack_name=pack_autocomplete)
    async def pack_open(self, interaction: discord.Interaction, pack_name: str, count: Optional[int]):
        user = self.datadriver.get_user(interaction.user.id)

        if user is None:
            await interaction.response.send_message("User does not exist in database.")
            return
        
        pack = self.datadriver.get_pack_by_name(pack_name)
        if pack is None:
            await interaction.response.send_message("Pack not found")
            return
        
        if not pack["name"] in user["packs"]:
            await interaction.response.send_message(f"You don't have pack {pack["name"]} in your inventory")
            return
        
        user["packs"].remove(pack_name)

        cards = self.datadriver.get_cards_from_list(pack["cards"])
        by_rarity = defaultdict(list)

        for card in cards:
            by_rarity[card["rarity"]].append(card)

        rarities = list(by_rarity.keys())
        weights = [RARITY_WEIGHT[r] for r in rarities]

        result = []
        for _ in range(5):
            chosen_rarity = random.choices(rarities, weights=weights, k=5)[0]
            chosen_card = random.choice(by_rarity[chosen_rarity])
            result.append(chosen_card)

        user["cards"] = user["cards"] + [card["name"] for card in result]
        self.datadriver.save_user(user_id=user["id"])

        pages = [card_to_container(card) for card in result]
        view = PageView(pages, interaction.user.id, f"You've opened {pack["name"]}")
        await interaction.response.send_message(view=view)

    @pack.command(name="list", description="List all available packs.")
    async def list_packs(self, interaction:discord.Interaction):
        packs = self.datadriver.packs

        names = ", ".join([p["name"] for p in packs])

        await interaction.response.send_message(f"Packs: {names}")

async def setup(bot):
    await bot.add_cog(Packs(bot, bot.datadriver))