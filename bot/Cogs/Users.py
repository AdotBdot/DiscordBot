from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.Utils.DataDriver import DataDriver
from bot.Utils.Enums import RARITY_EMOJI, RARITY_ORDER, RARITIES

from bot.Views.DataViews import card_to_container
from bot.Views.PageView import PageView
from bot.Views.SimpleView import SimpleView
from bot.Views.UpgradesView import UpgradesView

class Users(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver: DataDriver = datadriver

    # ====================
    # Autocomplete
    # ====================

    async def bundle_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        bundles = self.datadriver.bundle_cache
        choices = [app_commands.Choice(name=bundle, value=bundle) for bundle in bundles if current.lower() in bundle.lower()]
        
        return choices[:25]

    async def collection_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        collections = self.datadriver.collection_cache
        choices = [app_commands.Choice(name=collection, value=collection) for collection in collections if current.lower() in collection.lower()]
        
        return choices[:25]

    async def rarity_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        rarities = RARITIES
        choices = [app_commands.Choice(name=rarity, value=rarity) for rarity in rarities if current.lower() in rarity.lower()]
        
        return choices[:25]

    async def tag_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        tags = self.datadriver.tag_cache
        choices = [app_commands.Choice(name=tag, value=tag) for tag in tags if current.lower() in tag.lower()]
        
        return choices[:25]

    async def sort_by_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        sort_bys = ["RarityAscending", "NameAscending", "CollectionAscending", "BundleAscending", 
                    "RarityDescending", "NameDescending", "CollectionDescending", "BundleDescending"]
        choices = [app_commands.Choice(name=sort_by, value=sort_by) for sort_by in sort_bys if current.lower() in sort_by.lower()]
        
        return choices[:25]

    # ====================
    # Profile commands
    # ====================

    @app_commands.command(name="profile", description="Displays user profile.")
    async def profile(self, interaction: discord.Interaction):
        user = self.datadriver.get_user(interaction.user.id)

        if user is None:
            await interaction.response.send_message(f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return

        total_cards = self.datadriver.get_cards_count()
        container = discord.ui.Container(
                discord.ui.TextDisplay(content=f"### Collection\n**Size**: {len(user["cards"])}\n**Completion**: {len(set(user["cards"]))}/{total_cards}"),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content=f"### Currency\n**Cocoses**: {user["cash"]} 🥥\n**Melones**: {user["melons"]} 🍉")
            )

        view = SimpleView(
            author_id=interaction.user.id,
            content=container, 
            header=f"{interaction.user.mention}\n## Profile", 
            thumbnail=interaction.user.display_avatar.url
            )

        await interaction.response.send_message(view=view)

    # ====================
    # Inventory commands
    # ====================

    inventory = app_commands.Group(name="inventory", description="Inventory related commands.")

    @inventory.command(name="packs", description="Displays packs in users inventory.")
    async def inventory_packs(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message("Slow down. You don't have your profile yet. Use **/help** for more information.")
            return

        user_packs = self.datadriver.get_user_packs(user_id)

        if not user_packs:
            await interaction.response.send_message("You don't have any packs in your inventory.")
            return        

        #UI
        packs = {}
        for pack_name in user_packs:
            packs[pack_name] = packs.get(pack_name, 0) + 1

        msg = ""
        for key, value in packs.items():
            msg = msg + f"**{key}**: {value}x\n"

        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Packs"),
            discord.ui.TextDisplay(content=msg)
        )

        view = SimpleView(
            author_id=interaction.user.id,
            content=container, 
            header=f"{interaction.user.mention}\n## Inventory", 
            thumbnail=interaction.user.display_avatar.url
            )

        await interaction.response.send_message(view=view)

    @inventory.command(name="cards_gallery", description="Displays cards in user inventory")
    @app_commands.autocomplete(bundle=bundle_autocomplete, collection=collection_autocomplete, rarity=rarity_autocomplete, tag=tag_autocomplete, sort_by=sort_by_autocomplete)
    async def inventory_cards_gallery(self, interaction: discord.Interaction, 
                        bundle: Optional[str] = None, 
                        collection: Optional[str] = None,
                        rarity: Optional[str] = None,
                        tag: Optional[str] = None,
                        sort_by: Optional[str] = None
                        ):
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return

        df = self.datadriver.get_cards_by_traits(user_id=user_id, bundle=bundle, collection=collection, rarity=rarity, tag=tag)
        if df.empty:
            await interaction.response.send_message(content="You don't have any cards in your collection.")
            return
        
        # Sort cards
        if sort_by:
            reversed = "Descending" in sort_by

            if "Rarity" in sort_by:
                df = df.copy()
                df["rarity_rank"] = df["rarity"].map(RARITY_ORDER)
                df = df.sort_values("rarity_rank", ascending=not reversed)
            elif "Name" in sort_by:
                df = df.sort_values("name", ascending=not reversed)
            elif "Collection" in sort_by:
                df = df.sort_values("collection", ascending=not reversed)
            elif "Bundle" in sort_by:
                df = df.sort_values("bundle", ascending=not reversed)
            else:
                await interaction.response.send_message(content=f"Invalid key: {sort_by}")
                return

        # Count cards
        df_counts = df.groupby(level=0).size()
        df = df[~df.index.duplicated(keep="first")]

        # UI
        pages = []
        for key, value in df.iterrows():
            page = card_to_container(value)
            page.add_item(discord.ui.TextDisplay(content=f"**x{df_counts[key]}**")) # type: ignore
            pages.append(page)
        
        view = PageView(
            author_id=user_id,
            pages=pages, 
            header=f"{interaction.user.mention}\n## Collection", 
            thumbnail=interaction.user.display_avatar.url
            )
        
        await interaction.response.send_message(view=view)

    @inventory.command(name="cards_list", description="Displays cards in user inventory")
    @app_commands.autocomplete(bundle=bundle_autocomplete, collection=collection_autocomplete, rarity=rarity_autocomplete, tag=tag_autocomplete, sort_by=sort_by_autocomplete)
    async def inventory_cards_list(self, interaction: discord.Interaction, 
                        bundle: Optional[str] = None, 
                        collection: Optional[str] = None,
                        rarity: Optional[str] = None,
                        tag: Optional[str] = None,
                        sort_by: Optional[str] = None
                        ):
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return

        df = self.datadriver.get_cards_by_traits(user_id=user_id, bundle=bundle, collection=collection, rarity=rarity, tag=tag)
        if df.empty:
            await interaction.response.send_message(content="You don't have any cards in your collection.")
            return
        
        # Sort cards
        if sort_by:
            reversed = "Descending" in sort_by

            if "Rarity" in sort_by:
                df = df.copy()
                df["rarity_rank"] = df["rarity"].map(RARITY_ORDER)
                df = df.sort_values("rarity_rank", ascending=not reversed)
            elif "Name" in sort_by:
                df = df.sort_values("name", ascending=not reversed)
            elif "Collection" in sort_by:
                df = df.sort_values("collection", ascending=not reversed)
            elif "Bundle" in sort_by:
                df = df.sort_values("bundle", ascending=not reversed)
            else:
                await interaction.response.send_message(content=f"Invalid key: {sort_by}")
                return
        
        # Count cards
        df_counts = df.groupby(level=0).size()
        df = df[~df.index.duplicated(keep="first")]

        #UI
        pages = []
        for i in range(0, len(df), 20):
            chunk = df.iloc[i:i + 20]

            msg = "\n".join(
                f"**{RARITY_EMOJI[row["rarity"]]} {row["rarity"]}**: {key} **x{df_counts[key]}**"  # type: ignore
                for key, row in chunk.iterrows()
            )

            container = discord.ui.Container()
            container.add_item(discord.ui.TextDisplay(content=msg))
            pages.append(container)

        view = PageView(
            author_id=user_id, 
            pages=pages, 
            header=f"{interaction.user.mention}\n## Collection", 
            thumbnail=interaction.user.display_avatar.url
            )
        
        await interaction.response.send_message(view=view)

    # ====================
    # Upgrades commands
    # ====================

    @app_commands.command(name="upgrades", description="Manage your upgrades.")
    async def upgrades(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return

        view = UpgradesView(
            author_id=user_id, 
            datadriver=self.datadriver, 
            header=f"{interaction.user.mention}\n## Upgrades", 
            thumbnail=interaction.user.display_avatar.url
            )

        await interaction.response.send_message(view=view)
       
# Setup Cog
async def setup(bot):
    await bot.add_cog(Users(bot, bot.datadriver))