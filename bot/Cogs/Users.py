import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.Utils.Autocomplete import ac
from bot.Utils.DataDriver import DataDriver
from bot.Utils.Enums import RARITY_EMOJI, RARITY_ORDER, RARITIES, RARITY_VALUE

from bot.Views.DataViews import card_to_container
from bot.Views.PageView import PageView
from bot.Views.SimpleView import SimpleView
from bot.Views.UpgradesView import UpgradesView

class Users(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver: DataDriver = datadriver

        self.logger = logging.getLogger("Users")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.logger.addHandler(bot.logs_handler)

    # ====================
    # Profile commands
    # ====================

    @app_commands.command(name="profile", description="Displays user profile.")
    async def profile(self, interaction: discord.Interaction):
        # Checks
        user = self.datadriver.get_user(interaction.user.id)

        if user is None:
            await interaction.response.send_message(f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return

        # Process user collection
        df = self.datadriver.get_cards_by_names(user["cards"]) # type: ignore
        collection_value = df["rarity"].map(RARITY_VALUE).sum()
        total_cards = self.datadriver.get_cards_count()

        # UI
        container = discord.ui.Container(
                discord.ui.TextDisplay(content=f"### Collection\n**Size**: {len(user["cards"])}\n**Completion**: {len(set(user["cards"]))}/{total_cards}\n**Value**: {collection_value} 🥥"),
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
        # Checks
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

    # ====================
    # Collection commands
    # ====================

    collection = app_commands.Group(name="collection", description="User collection related commands.", parent=inventory)

    @collection.command(name="gallery", description="Displays cards in user inventory")
    @app_commands.autocomplete(bundle=ac("bundle"), collection=ac("collection"), rarity=ac("rarity"), tag=ac("tag"), sort_by=ac("sort_by"))
    async def inventory_cards_gallery(self, interaction: discord.Interaction, bundle: Optional[str] = None, collection: Optional[str] = None,
                        rarity: Optional[str] = None, tag: Optional[str] = None, sort_by: Optional[str] = None):
        # Checks
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

    @collection.command(name="list", description="Lists cards in user inventory")
    @app_commands.autocomplete(bundle=ac("bundle"), collection=ac("collection"), rarity=ac("rarity"), tag=ac("tag"), sort_by=ac("sort_by"))
    async def inventory_cards_list(self, interaction: discord.Interaction, bundle: Optional[str] = None, collection: Optional[str] = None,
                        rarity: Optional[str] = None, tag: Optional[str] = None, sort_by: Optional[str] = None):
        # Checks
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
                f"{RARITY_EMOJI[row["rarity"]]} {key} **x{df_counts[key]}**" if df_counts[key] > 1 else f"{RARITY_EMOJI[row["rarity"]]} {key}" # type: ignore
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

    @collection.command(name="completion", description="Displays selected collection completion")
    @app_commands.autocomplete(collection=ac("collection"))
    async def inventory_collection_completion(self, interaction: discord.Interaction, collection: Optional[str] = None):
        # Checks
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return

        # Process user cards
        user_cards = self.datadriver.get_cards_by_traits(user_id=user_id, collection=collection)
        
        all_cards = self.datadriver.get_cards_by_traits(collection=collection)
        if all_cards.empty:
            await interaction.response.send_message("Collection not found.")
            return
        
        total_by_rarity = (all_cards["rarity"].value_counts())
        owned_by_rarity = (user_cards.reset_index().drop_duplicates(subset="name")["rarity"].value_counts())

        lines = []
        total_cards = 0
        owned_cards = 0

        for rarity in RARITIES:
            total = total_by_rarity.get(rarity, 0)
            owned = owned_by_rarity.get(rarity, 0)

            total_cards += total
            owned_cards += owned

            lines.append(f"{RARITY_EMOJI[rarity]} **{rarity}**: {owned}/{total}")

        percentage = (owned_cards / total_cards * 100 if total_cards > 0 else 0)
        
        # UI
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {collection}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=f"**Progress**: {percentage:.2f}%"),
            discord.ui.TextDisplay(content="\n".join(lines))
        )

        view = SimpleView(
            author_id=user_id,
            content=container,
            header=f"{interaction.user.mention}\n## Collection",
            thumbnail=interaction.user.display_avatar.url
            )
        await interaction.response.send_message(view=view)


    # ====================
    # Upgrades commands
    # ====================

    @app_commands.command(name="upgrades", description="Manage your upgrades.")
    async def upgrades(self, interaction: discord.Interaction):
        # Checks
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return

        # UI
        view = UpgradesView(
            author_id=user_id, 
            datadriver=self.datadriver, 
            header=f"{interaction.user.mention}\n## Upgrades", 
            thumbnail=interaction.user.display_avatar.url
            )
        
        await interaction.response.send_message(view=view)
       
    # ====================
    # Lock commands
    # ====================

    lock = app_commands.Group(name="lock", description="Locks related commands.")

    @lock.command(name="collection", description="Locks selected collection.")
    @app_commands.autocomplete(collection=ac("collection"))
    async def lock_collection(self, interaction: discord.Interaction, collection: str):
        # Checks
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return

        if collection not in self.datadriver.collection_cache:
            await interaction.response.send_message(content=f"Collection: **{collection}** not found.")
            return
        
        # Lock collection
        user_locks = self.datadriver.get_user_locked_collections(user_id)
        user_locks.append(collection)
        self.datadriver.set_user_locked_collections(user_id, user_locks)

        # Logs
        self.logger.info(f"{user_id} locked collection: '{collection}'")

        # UI
        await interaction.response.send_message(f"Successfully locked collection: **{collection}**")

    @lock.command(name="rarity", description="Locks selected rarity.")
    @app_commands.autocomplete(rarity=ac("rarity"))
    async def lock_rarity(self, interaction: discord.Interaction, rarity: str):
        # Checks
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return

        if rarity not in RARITIES:
            await interaction.response.send_message(content=f"Rarity **{rarity}** does not exists.")
            return
        
        # Lock rarity
        user_locks = self.datadriver.get_user_locked_rarities(user_id)
        user_locks.append(rarity)
        self.datadriver.set_user_locked_rarities(user_id, user_locks)

        # Logs
        self.logger.info(f"{user_id} locked rarity: '{rarity}'")

        # UI
        await interaction.response.send_message(f"Successfully locked rarity: **{rarity}**")

    unlock = app_commands.Group(name="unlock", description="Unlocks related commands.")

    @unlock.command(name="collection", description="Unlocks selected collection.")
    @app_commands.autocomplete(collection=ac("collection"))
    async def unlock_collection(self, interaction: discord.Interaction, collection: str):
        # Checks
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return

        if collection not in self.datadriver.collection_cache:
            await interaction.response.send_message(content=f"Collection: **{collection}** not found.")
            return
        
        # Unlock collection
        user_locks = self.datadriver.get_user_locked_collections(user_id)
        user_locks.remove(collection)
        self.datadriver.set_user_locked_collections(user_id, user_locks)

        # Logs
        self.logger.info(f"{user_id} unlocked collection: '{collection}'")

        # UI
        await interaction.response.send_message(f"Successfully unlocked collection: **{collection}**")

    @unlock.command(name="rarity", description="Unlocks selected rarity.")
    @app_commands.autocomplete(rarity=ac("rarity"))
    async def unlock_rarity(self, interaction: discord.Interaction, rarity: str):
        # Checks
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return

        if rarity not in RARITIES:
            await interaction.response.send_message(content=f"Rarity **{rarity}** does not exists.")
            return
        
        # Unlock rarity
        user_locks = self.datadriver.get_user_locked_rarities(user_id)
        user_locks.remove(rarity)
        self.datadriver.set_user_locked_rarities(user_id, user_locks)

        # Logs
        self.logger.info(f"{user_id} unlocked rarity: '{rarity}'")

        # UI
        await interaction.response.send_message(f"Successfully unlocked rarity: **{rarity}**")

    @lock.command(name="list", description="Displays locked rarities and collections.")
    async def lock_list(self, interaction: discord.Interaction):
        # Checks
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(content=f"Slow down. You don't have your profile yet. Use **/help** for more information.")
            return
        
        # Query locked rarities and collections
        locked_rarities = self.datadriver.get_user_locked_rarities(user_id)
        locked_collections = self.datadriver.get_user_locked_collections(user_id)

        # UI
        rarities_msg = ["### Locked rarities"]
        if not locked_rarities:
            rarities_msg.append("None")
        else:
            for rarity in locked_rarities:
                rarities_msg.append(f"{RARITY_EMOJI[rarity]} **{rarity}**")

        collection_msg = ["### Locked collections"]
        if not locked_collections:
            collection_msg.append("None")
        else:
            collection_msg += locked_collections

        rarities_msg = '\n'.join(rarities_msg)
        collection_msg = '\n'.join(collection_msg)

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=rarities_msg),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=collection_msg)
        )

        view = SimpleView(
            author_id=user_id,
            content=container,
            header=f"{interaction.user.mention}\n## Locks",
            thumbnail=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(view=view)

# Setup Cog
async def setup(bot):
    await bot.add_cog(Users(bot, bot.datadriver))