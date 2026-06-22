import random
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.Utils.DataDriver import DataDriver
from bot.Utils.Enums import BASE_RARITY_WEIGHT, RARITY_EMOJI

from bot.Views.DataViews import card_to_container
from bot.Views.PageView import PageView
from bot.Views.SimpleView import SimpleView

class Packs(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver = datadriver

    # ====================
    # Autocomplete
    # ====================

    async def pack_autocomplete(self, interaction: discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
        packs = self.datadriver.packs_cache
        choices = [app_commands.Choice(name=pack, value=pack) for pack in packs if current.lower() in pack.lower()]
        
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
    # Pack commands
    # ====================

    pack = app_commands.Group(name="pack", description="Pack related commands.")

    @pack.command(name="list", description="Lists all available packs.")
    async def pack_list(self, interaction:discord.Interaction):
        packs = self.datadriver.packs_cache

        msg = "\n".join(f"**{p}**" for p in packs)

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=msg)
        )

        view = SimpleView(
            author_id=interaction.user.id,
            content=container,
            header="## Available Packs"
        )

        await interaction.response.send_message(view=view)

    @pack.command(name="info", description="Displays information about pack.")
    @app_commands.autocomplete(pack_name=pack_autocomplete)
    async def pack_info(self, interaction: discord.Interaction, pack_name: str):
        if not self.datadriver.pack_exist(pack_name):
            await interaction.response.send_message("Pack not found.")
            return
        
        pack = self.datadriver.get_pack_by_name(pack_name)

        pack_cards = self.datadriver.get_cards_by_names(pack["cards"]) # type: ignore

        all_rarities = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic", "Divine"]
        rarity_count = pack_cards["rarity"].value_counts().reindex(all_rarities, fill_value=0)

        msg = "\n".join(
            f"{RARITY_EMOJI[rarity]} **{rarity}**: {count}" # type: ignore
            for rarity, count in rarity_count.items()
        )

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### Cards: {len(pack["cards"])}"), # type: ignore
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=msg)
        )

        view = SimpleView(
            author_id=interaction.user.id,
            content=container,
            header=f"## {pack_name}"
        )

        await interaction.response.send_message(view=view)

    @pack.command(name="open", description="Opens pack from your inventory.")
    @app_commands.autocomplete(pack_name=user_pack_autocomplete)
    async def pack_open(self, interaction: discord.Interaction, pack_name: str, count: Optional[int]):
        user_id = interaction.user.id
        
        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message("User does not exist in database.")
            return
        
        if not self.datadriver.pack_exist(pack_name):
            await interaction.response.send_message("Pack not found.")
            return
        
        open_count = count or 1
        user_packs = self.datadriver.get_user_packs(user_id)
        
        if user_packs.count(pack_name) < open_count:
            await interaction.response.send_message(f"You don't have enough **{pack_name}** in your inventory")
            return

        # Remove pack from user inventory
        for _ in range(open_count):
            user_packs.remove(pack_name)

        self.datadriver.set_user_packs(user_id, user_packs)

        # Get cards from pack
        pack_cards = self.datadriver.get_pack_cards(pack_name)
        cards = self.datadriver.get_cards_by_names(pack_cards)

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
        user_cards = self.datadriver.get_user_cards(user_id)
        user_cards.extend([card.name for card in result])
        self.datadriver.set_user_cards(user_id, user_cards)

        pages = [card_to_container(card) for card in result]
        view = PageView(
            pages=pages, 
            author_id=interaction.user.id, 
            header=f"You've opened **{pack_name}**"
            )
        
        await interaction.response.send_message(view=view)

async def setup(bot):
    await bot.add_cog(Packs(bot, bot.datadriver))