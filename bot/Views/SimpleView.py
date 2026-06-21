import discord

class SimpleView(discord.ui.LayoutView):
    def __init__(self, author_id: int,  content: discord.ui.Container, header: str|None=None, thumbnail: str|None=None):
        super().__init__()
        
        self.author_id = author_id

        # Header
        self.header = None
        if header:
            if thumbnail:
                self.header = discord.ui.Container(
                    discord.ui.Section(
                        discord.ui.TextDisplay(content=header),
                        accessory=discord.ui.Thumbnail(media=thumbnail)
                    )
                )
            else:
                self.header = discord.ui.Container(discord.ui.TextDisplay(content=header))

        self.container = content
        if self.header:
            self.add_item(self.header)
        self.add_item(self.container)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.author_id