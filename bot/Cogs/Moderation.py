import logging

import discord
from discord.ext import commands
from discord import app_commands

from bot.Utils.Autocomplete import ac
from bot.Utils.DataDriver import DataDriver
from bot.Utils.Permissions import admin_only

from bot.Views.SimpleView import SimpleView

class Moderation(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver = datadriver

        self.logger = logging.getLogger("Moderation")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.logger.addHandler(bot.logs_handler)

    # ====================
    # General commands
    # ====================

    # TODO: Implement setup command
    @app_commands.command(name="setup", description="Setups bot on server.")
    @admin_only()
    async def setup(self, interaction: discord.Interaction):
        await interaction.response.send_message("**/setup** is not implemented yet.")

    @app_commands.command(name="reload_module", description="Reloads module.")
    @admin_only()
    async def reload_module(self, interaction: discord.Interaction, module: str):
        ext = f"bot.Cogs.{module}"
        try:
            await self.bot.reload_extension(ext)
            await self.bot.tree.sync()
            await interaction.response.send_message(f"Reloaded '{ext}'.")
        except Exception as e:
            await interaction.response.send_message(f"Error reloading module {ext}: '{e}'.")

    @app_commands.command(name="update_users", description="Forces users database update.")
    @admin_only()
    async def update_users(self, interaction: discord.Interaction):
        try:
            for user_id in self.datadriver.users.index:
                self.datadriver.save_user(user_id)

            await interaction.response.send_message(f"Updated user database.")
        except Exception as e:
            await interaction.response.send_message(f"Error updating users: '{e}'.")

    @app_commands.command(name="stats", description="Displays bot stats.")
    @admin_only()
    async def status(self, interaction: discord.Interaction):
        # Query bot status
        total_seconds = int(self.bot.uptime.total_seconds())

        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        # UI
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"**Uptime**: {days}d {hours}h {minutes}m {seconds}s"),
            discord.ui.Separator(visible=True),
            discord.ui.TextDisplay(content=f"**Users**: {len(self.datadriver.users)}"),
            discord.ui.TextDisplay(content=f"**Bundles**: {len(self.datadriver.bundle_cache)}\n**Collections**: {len(self.datadriver.collection_cache)}\n**Cards**: {self.datadriver.get_cards_count()}\n**Packs**: {len(self.datadriver.packs)}")
        )

        view = SimpleView(
            author_id=interaction.user.id,
            content=container, 
            header="## Bot stats")
        
        await interaction.response.send_message(view=view)

    @app_commands.command(name="reload_cards", description="Reloads cards database.")
    @admin_only()
    async def reload_cards(self, interaction: discord.Interaction):
        # Reload cards and rebuild cache
        self.datadriver.load_cards()
        self.datadriver.load_packs()
        self.datadriver.init_cache()

        # UI
        await interaction.response.send_message("Reloaded cards database.")

    @app_commands.command(name="refresh_daily", description="Refreshes daily rewards.")
    @admin_only()
    async def refresh_daily(self, interaction: discord.Interaction):
        self.datadriver.refresh_daily()
        self.datadriver.save_config()

        # UI
        await interaction.response.send_message("Refreshed dailies.")

    # ====================
    # Give commands
    # ====================

    give = app_commands.Group(name="give", description="Give related commands.")
    
    @give.command(name="card", description="Gives card to user collection.")
    @admin_only()
    @app_commands.autocomplete(card=ac("card"))
    async def give_card(self, interaction: discord.Interaction, target_user: discord.Member, card: str):
        # Checks
        target_user_id = target_user.id

        if not self.datadriver.user_exist(target_user_id):
            await interaction.response.send_message("User does not exist in database.")
            return
        
        if not self.datadriver.card_exist(card):
            await interaction.response.send_message("Card not found.")
            return
        
        # Give card to user
        target_user_cards = self.datadriver.get_user_cards(target_user_id)
        target_user_cards.append(card) # type: ignore
        self.datadriver.set_user_cards(target_user_id, target_user_cards)

        # Logs
        self.logger.info(f"Gave card: '{card}' to {target_user_id}")

        await interaction.response.send_message(f"Gave **{card}** to {target_user.mention}")

    @give.command(name="pack", description="Gives pack to user inventory.")
    @admin_only()
    @app_commands.autocomplete(pack=ac("pack"))
    async def give_pack(self, interaction: discord.Interaction, target_user: discord.Member, pack: str, count: int):
        # Checks
        target_user_id = target_user.id

        if not self.datadriver.user_exist(target_user_id):
            await interaction.response.send_message(f"User does not exist in database.")
            return
        
        if not self.datadriver.pack_exist(pack):
            await interaction.response.send_message("Pack not found.")
            return
        
        # Give pack to user
        target_user_packs = self.datadriver.get_user_packs(target_user_id)
        for _ in range(count):
            target_user_packs.append(pack) # type: ignore

        self.datadriver.set_user_packs(target_user_id, target_user_packs)

        # Logs
        self.logger.info(f"Gave {count} pack(s): '{pack}' to {target_user_id}")

        # UI
        await interaction.response.send_message(f"Gave {count} pack(s): {pack} to user {target_user.mention}")

    @give.command(name="cocoses", description="Gives Cocoses to user inventory.")
    @admin_only()
    async def give_cocoses(self, interaction: discord.Interaction, target_user: discord.Member, cocoses: int):
        # Checks
        target_user_id = target_user.id

        if not self.datadriver.user_exist(target_user_id):
            await interaction.response.send_message(f"User does not exist in database.")
            return
        
        # Give cocoses to user
        self.datadriver.users.at[target_user_id, "cash"] += cocoses # type: ignore
        self.datadriver.mark_dirty(target_user_id)
        
        # Logs
        self.logger.info(f"Gave {cocoses} cocoses to {target_user_id}")

        # UI
        await interaction.response.send_message(f"Gave {cocoses} 🥥 to user {target_user.mention}")

    @give.command(name="melones", description="Gives Melones to user inventory.")
    @admin_only()
    async def give_melones(self, interaction: discord.Interaction, target_user: discord.Member, melones: int):
        # Checks
        target_user_id = target_user.id

        if not self.datadriver.user_exist(target_user_id):
            await interaction.response.send_message(f"User does not exist in database.")
            return
        
        # Give melones to user
        self.datadriver.users.at[target_user_id, "melons"] += melones # type: ignore
        self.datadriver.mark_dirty(target_user_id)
        
        # Logs
        self.logger.info(f"Gave {melones} melones to {target_user_id}")

        # UI
        await interaction.response.send_message(f"Gave {melones} 🍉 to user {target_user.mention}")

# Setup Cog
async def setup(bot):
    await bot.add_cog(Moderation(bot, bot.datadriver))