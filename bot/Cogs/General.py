import logging

import discord
from discord.ext import commands
from discord import app_commands

from bot.Views.PageView import PageView

from bot.Utils.DataDriver import DataDriver

class General(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver = datadriver

        self.logger = logging.getLogger("General")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.logger.addHandler(bot.logs_handler)

    def format_command(self, command: app_commands.Command | app_commands.Group, indent: int=0) -> list[str]:
        lines = []

        prefix = "    " * indent

        if indent == 0:
            name = f"/{command.name}"
        else:
            name = command.name

        if isinstance(command, app_commands.Group):
            lines.append(f"{prefix}**{name}** - {command.description}")

            for child in command._children.values():
                lines.extend(self.format_command(child, indent + 1))

        else:
            lines.append(f"{prefix}**{name}** - {command.description or 'No description.'}")

        return lines

    # ====================
    # General commands
    # ====================

    @app_commands.command(name="lesgo", description="Creates user profile.")
    async def lesgo(self, interaction:discord.Interaction):
        # Checks
        if self.datadriver.user_exist(interaction.user.id):
            await interaction.response.send_message("You already have profile created.")
            return
        
        self.datadriver.create_user(user_id=interaction.user.id)

        # UI
        await interaction.response.send_message("Your profile has been created.")

    @app_commands.command(name="help", description="Displays help.")
    async def help(self, interaction: discord.Interaction):
        # UI
        pages = []

        for cog_name, cog in self.bot.cogs.items():
            commands = cog.get_app_commands()

            if not commands:
                continue

            lines = [
                f"### {cog_name}"
            ]

            for command in commands:
                lines.extend(self.format_command(command))

            container = discord.ui.Container()
            container.add_item(
                discord.ui.TextDisplay(
                    content="\n".join(lines)
                )
            )

            pages.append(container)

        if not pages:
            await interaction.response.send_message("No commands available.")
            return

        view = PageView(
            author_id=interaction.user.id, 
            pages=pages, 
            header="## Help")

        await interaction.response.send_message(view=view)

# Setup Cog
async def setup(bot):
    await bot.add_cog(General(bot, bot.datadriver))