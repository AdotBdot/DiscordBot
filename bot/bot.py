import logging
import discord
from discord.ext import commands
from .Data import JsonDeserializer

from .Views import PageView

from .Data import Card

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

    async def on_ready(self) -> None:
        self.logger.info(f'Logged in as: {self.user}')

    async def setup_hook(self) -> None:
        
        @self.tree.command(name="test", description="A test command")
        async def test(interation: discord.Interaction):
            data = JsonDeserializer.read_json("data/test.json")
            cards = JsonDeserializer.to_card_list(data)
            pages = [card.to_embed() for card in cards]
            view = PageView.PageView(pages, interation.user.id)
            await interation.response.send_message(embed=pages[0], view=view)

        await self.tree.sync()

    def run(self, token) -> None:
        super().run(token, log_handler=None)

