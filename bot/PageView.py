import discord

class PageView(discord.ui.View):
    def __init__(self, pages, author_id):
        super().__init__(timeout=60)
        self.pages = pages
        for page in self.pages:
            page.set_footer(text=f"({self.pages.index(page) + 1}/{len(self.pages)})")
        self.current_page = 0
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.author_id
    
    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.primary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            embed = self.pages[self.current_page]
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            embed = self.pages[self.current_page]
            await interaction.response.edit_message(embed=embed, view=self)