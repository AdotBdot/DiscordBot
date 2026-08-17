import asyncio
import datetime
import logging
from pathlib import Path
import typing
import traceback

import discord
from discord.ext import commands

# Data
from bot.Utils.Autocomplete import AutocompleteService
from bot.Utils.DataDriver import DataDriver, DataDriverScheduler

class Bot(commands.Bot):
    _uptime: datetime.datetime = datetime.datetime.utcnow()

    def __init__(self, logs_handler, file_handler):
        intents = discord.Intents.all()
        super().__init__(intents=intents, command_prefix=">")

        self.logs_handler = logs_handler
        self.file_handler = file_handler

        self.logger = logging.getLogger("Bot")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.logger.addHandler(logs_handler)
        self.logger.addHandler(file_handler)

        self.datadriver: DataDriver = DataDriver(logs_handler, file_handler)
        self.datadriver.initialize_database()

        self.autocomplete: AutocompleteService = AutocompleteService(self.datadriver)

        self.scheduler = DataDriverScheduler(self.datadriver)

    async def on_ready(self) -> None:
        self.logger.info(f'Logged in as: {self.user}')

        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="/help"))

    async def on_error(self, event_method: str, *args:typing.Any, **kwards: typing.Any) -> None:
        self.logger.info(f"An error has occurred in {event_method}.\n{traceback.format_exc()}")

    async def setup_hook(self) -> None:
        asyncio.create_task(self.scheduler.run())

        await self.load_extensions()
        
        await self.tree.sync()
        self.logger.info("Sync Done")

    async def load_extensions(self) -> None:
        for file in Path("bot/Cogs").glob("*.py"):
            if file.name == "__init__.py":
                continue
            
            ext = f"bot.Cogs.{file.stem}"

            try:
                await self.load_extension(ext)
                cog = self.get_cog(file.stem.capitalize())

                if cog:
                    commands_list = cog.get_app_commands()
                    commands_msg = ", ".join([cmd.name for cmd in commands_list])
                    self.logger.info(f"Loaded {ext} with {len(commands_list)} command(s): {commands_msg}")
            except Exception as e:
                self.logger.error(f"Failed loading {ext}: {e}")
        
    @property
    def uptime(self) -> datetime.timedelta:
        return datetime.datetime.utcnow() - self._uptime

    def run(self, token) -> None:
        super().run(token, log_handler=None)
