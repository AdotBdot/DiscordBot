import datetime
import logging
from pathlib import Path
import typing
import traceback

import discord
from discord.ext import commands

# Data
from bot.Utils.DataDriver import DataDriver

# Cogs
from bot.Cogs.General import General

GUILD_ID = discord.Object(id=786999655413579807)

class Bot(commands.Bot):
    _uptime: datetime.datetime = datetime.datetime.utcnow()

    def __init__(self, logs_handler):
        intents = discord.Intents.all()
        super().__init__(intents=intents, command_prefix=">")

        self.logger = logging.getLogger("Bot")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.logger.addHandler(logs_handler)

        self.datadriver = DataDriver(logs_handler)
        self.datadriver.initialize_database()

    async def on_ready(self) -> None:
        self.logger.info(f'Logged in as: {self.user}')

    async def on_error(self, event_method: str, *args:typing.Any, **kwards: typing.Any) -> None:
        self.logger.info(f"An error has occurred in {event_method}.\n{traceback.format_exc()}")

    async def setup_hook(self) -> None:
        await self.load_extensions()
        await self.tree.sync(guild=GUILD_ID)

    async def load_extensions(self) -> None:
        for file in Path("bot/Cogs").glob("*.py"):
            if file.name == "__init__.py":
                continue
            
            ext = f"bot.Cogs.{file.stem}"

            try:
                await self.load_extension(ext)
                self.logger.info(f"Loaded {ext}")
            except Exception as e:
                self.logger.error(f"Failed loading {ext}: e")
        
    @property
    def uptime(self) -> datetime.timedelta:
        return datetime.datetime.utcnow() - self._uptime

    def run(self, token) -> None:
       # try:
            super().run(token, log_handler=None)
       # except:
         #   self.logger.info("Exiting...")
        #    exit()
