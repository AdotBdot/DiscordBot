import discord

class PageView(discord.ui.LayoutView):
    def __init__(self, author_id: int, pages: list[discord.ui.Container], header: str|None=None, thumbnail: str|None=None):
        super().__init__()

        self.pages = pages
        self.author_id = author_id
        self.current_page = 0
        self.header = None

        # Header
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

        # Container
        self.container = self.pages[self.current_page]

        # Buttons
        self.prev_btn = discord.ui.Button(
                label="Prev",
                style = discord.ButtonStyle.primary,
                custom_id="prev"
            )
        self.next_btn = discord.ui.Button(
                label="Next",
                style = discord.ButtonStyle.primary,
                custom_id="next"
            )
        
        self.prev_btn.callback = self.previous_page
        self.next_btn.callback = self.next_page

        self.actions = discord.ui.ActionRow(self.prev_btn, self.next_btn)

        # Footer
        self.footer = discord.ui.TextDisplay(content=f"Page {self.current_page+1}/{len(self.pages)}")

        self.update_view()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.author_id
    
    def update_view(self):
        # Button states
        self.prev_btn.disabled = self.current_page == 0
        self.next_btn.disabled = self.current_page == len(self.pages) - 1

        # Replace container
        self.container = self.pages[self.current_page]

        # Update footer
        self.footer = discord.ui.TextDisplay(content=f"Page {self.current_page+1}/{len(self.pages)}")

        # Update view
        self.clear_items()
        if self.header:
            self.add_item(self.header)
        self.add_item(self.container)
        self.add_item(self.footer)
        self.add_item(self.actions)
    
    async def previous_page(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1

        self.update_view()
        await interaction.response.edit_message(view=self)

    async def next_page(self, interaction: discord.Interaction):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1

        self.update_view()
        await interaction.response.edit_message(view=self)