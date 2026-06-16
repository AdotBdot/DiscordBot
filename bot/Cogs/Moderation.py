import discord
from discord.ext import commands
from discord import app_commands

# Utils
from bot.Utils.Permissions import admin_only, owner_only
from bot.Utils.DataDriver import DataDriver

class Moderation(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver = datadriver

    # TODO: Implement setup command
    @app_commands.command(name="setup", description="Setups bot on server.")
    @admin_only()
    async def setup(self, interaction: discord.Interaction):
        await interaction.response.send_message("ok")

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

    @app_commands.command(name="update_users", description="Forces user database update.")
    @admin_only()
    async def update_users(self, interaction: discord.Interaction):
        try:
            self.datadriver.update_users()
            await interaction.response.send_message(f"Updated user database.")
        except Exception as e:
            await interaction.response.send_message(f"Error updating users: '{e}'.")

    @app_commands.command(name="uptime", description="Display bot uptime")
    @admin_only()
    async def uptime(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"{self.bot.uptime}")

    # /config group
    # config = discord.app_commands.Group(name="config", description="Bot configuration commands.")

    # @config.command(name="set")
    # async def set_config(self, interaction: discord.Interaction, key:str, value:str):
    #     pass

async def setup(bot):
    await bot.add_cog(Moderation(bot, bot.datadriver))