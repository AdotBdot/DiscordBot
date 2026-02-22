import logging
from xml.sax import handler
import discord
from discord.ext import commands

from . import PageView

def create_embed(num):
    embed = discord.Embed(description=num)
    return embed

class Bot(discord.Client):
    def __init__(self, logs_handler):
        intents = discord.Intents.all()
        super().__init__(intents=intents)

        self.logger = logging.getLogger("Bot")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.logger.addHandler(logs_handler)


        self.tree = discord.app_commands.CommandTree(self)

    async def on_ready(self):
        self.logger.info(f'Logged in as: {self.user}')

    async def setup_hook(self) -> None:
        
        @self.tree.command(name="test", description="A test command")
        async def test(interation: discord.Interaction):
            pages = [create_embed(i) for i in range(1, 6)]
            view = PageView.PageView(pages, interation.user.id)
            await interation.response.send_message(embed=pages[0], view=view)

        await self.tree.sync()

    def run(self, token):
        super().run(token, log_handler=None)

