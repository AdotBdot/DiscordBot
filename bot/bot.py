import discord
from discord.ext import commands
import PageView

def create_embed(num):
    embed = discord.Embed(description=num)
    return embed

class Bot(discord.Client):
    def __init__(self, prefix='!'):
        intents = discord.Intents.all()
        super().__init__(intents=intents)

        self.tree = discord.app_commands.CommandTree(self)

    async def on_ready(self):
        print(f'Logged in as: {self.user}')

    def run(self, token):
        super().run(token)

    async def setup_hook(self) -> None:
        
        @self.tree.command(name="test", description="A test command")
        async def test(interation: discord.Interaction):
            pages = [create_embed(i) for i in range(1, 6)]
            view = PageView.PageView(pages, interation.user.id)
            await interation.response.send_message(embed=pages[0], view=view)

        await self.tree.sync()

