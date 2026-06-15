import discord
from discord.ext import commands

from bot.Utils.Permissions import admin_only

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO: Implement setup command
    @discord.app_commands.command(name="setup", description="Setups bot on server")
    @admin_only()
    async def setup(self, interaction:discord.Interaction):
        pass

    @discord.app_commands.command(name="reload_module", description="Reloads module")
    @admin_only()
    async def reload_module(self, interaction:discord.Interaction, module: str):
        ext = f"bot.Cogs.{module}"
        try:
            await self.bot.reload_extension(ext)
            await self.bot.tree.sync()
            await interaction.response.send_message(f"Reloaded '{ext}'", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error reloading module {ext}: {e}", ephemeral=True)
        pass

    @discord.app_commands.command(name="uptime", description="Display bot uptime")
    @admin_only()
    async def uptime(self, interaction:discord.Interaction):
        await interaction.response.send_message(f"{self.bot.uptime}")

    # /config group
    config = discord.app_commands.Group(name="config", description="Bot configuration commands.")

    @config.command(name="set")
    async def set_config(self, interaction: discord.Interaction, key:str, value:str):
        pass

async def setup(bot):
    await bot.add_cog(Moderation(bot))