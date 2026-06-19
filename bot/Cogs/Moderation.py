import discord
from discord.ext import commands
from discord import app_commands

# Utils
from bot.Utils.Permissions import admin_only, owner_only
from bot.Utils.DataDriver import DataDriver

from bot.Views.SimpleView import SimpleView

class Moderation(commands.Cog):
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
            for user_id in self.datadriver.users_df.index:
                self.datadriver.update_user(user_id)

            await interaction.response.send_message(f"Updated user database.")
        except Exception as e:
            await interaction.response.send_message(f"Error updating users: '{e}'.")

    @app_commands.command(name="stats", description="Displays bot stats.")
    @admin_only()
    async def status(self, interaction: discord.Interaction):
        total_seconds = int(self.bot.uptime.total_seconds())

        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"**Uptime**: {days}d {hours}h {minutes}m {seconds}s"),
            discord.ui.Separator(visible=True),
            discord.ui.TextDisplay(content=f"**Users**: {len(self.datadriver.users_df)}"),
            discord.ui.TextDisplay(content=f"**Bundles**: {len(self.datadriver.bundle_cache)}\n**Collections**: {len(self.datadriver.collection_cache)}\n**Cards**: {self.datadriver.get_cards_count()}\n**Packs**: {len(self.datadriver.packs_df)}")
        )

        view = SimpleView(content=container, header="## Bot stats")
        await interaction.response.send_message(view=view)

    # ====================
    # Give commands
    # ====================

    give = app_commands.Group(name="give", description="Gives item to user inventory.")
    
    @give.command(name="pack")
    @admin_only()
    @app_commands.autocomplete(pack=pack_autocomplete)
    async def give_pack(self, interaction: discord.Interaction, target_user: discord.Member, pack: str, count: int):
        user = self.datadriver.get_user(target_user.id)

        if user is None:
            await interaction.response.send_message(f"User does not exist in database.")
            return
        
        user_packs = user["packs"]

        for _ in range(count):
            user_packs.append(pack)

        self.datadriver.users_df.at[interaction.user.id, "packs"] = user_packs # type: ignore

        self.datadriver.save_user(interaction.user.id)
        
        await interaction.response.send_message(f"Gave {count} pack(s): {pack} to user {target_user.mention}")

    @give.command(name="cocoses", description="Gives Cocoses to user inventory.")
    @admin_only()
    async def give_cocoses(self, interaction: discord.Interaction, target_user: discord.Member, cocoses: int):
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(f"User does not exist in database.")
            return
        
        self.datadriver.users_df.at[user_id, "cash"] += cocoses # type: ignore
        self.datadriver.save_user(user_id)
        
        await interaction.response.send_message(f"Gave {cocoses} 🥥 to user {target_user.mention}")

    @give.command(name="melones", description="Gives Melones to user inventory.")
    @admin_only()
    async def give_melones(self, interaction: discord.Interaction, target_user: discord.Member, melones: int):
        user_id = interaction.user.id

        if not self.datadriver.user_exist(user_id):
            await interaction.response.send_message(f"User does not exist in database.")
            return
        
        self.datadriver.users_df.at[user_id, "melons"] += melones # type: ignore
        self.datadriver.save_user(user_id)
        
        await interaction.response.send_message(f"Gave {melones} 🍉 to user {target_user.mention}")

# Setup Cog
async def setup(bot):
    await bot.add_cog(Moderation(bot, bot.datadriver))