from typing import Optional

import discord
from discord.ext import commands

from bot.Utils.DataDriver import DataDriver
from bot.Utils.Enums import UPGRADES_INFO

class UpgradeButton(discord.ui.Button):
    def __init__(self, upgrade_name: str, view: UpgradesView, label: str="Upgrade"):
        super().__init__(label=label, style=discord.ButtonStyle.primary)

        self.upgrade_name = upgrade_name
        self.upgrades_view = view

    async def callback(self, interaction: discord.Interaction):
        await self.upgrades_view.upgrade(interaction, self.upgrade_name)


class UpgradesView(discord.ui.LayoutView):

    def __init__(self, author_id: int, datadriver: DataDriver, header: Optional[str]=None, thumbnail: Optional[str]=None):
        super().__init__()

        self.datadriver = datadriver
        self.author_id = author_id
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

        self.update_view()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.author_id

    def get_upgrades(self) -> dict[str, int]:
        upgrades = self.datadriver.users_df.at[self.author_id, "upgrades"]

        return upgrades or {} # type: ignore

    def update_view(self):
        self.clear_items()

        # Header
        if self.header:
            self.add_item(self.header)

        # Content
        container = discord.ui.Container()
        upgrades = self.get_upgrades()

        for name, level in upgrades.items():
            section = discord.ui.Section(
                discord.ui.TextDisplay(content=f"**{UPGRADES_INFO[name]["display_name"]}**: {level}\n{UPGRADES_INFO[name]["description"]}"),
                accessory=UpgradeButton(
                    upgrade_name=name,
                    view=self,
                    label="1000🥥"
                )
            )

            container.add_item(section)

        self.add_item(container)

    async def upgrade(self, interaction: discord.Interaction, upgrade_name: str):
        try:
            upgrades = self.get_upgrades()

            upgrades[upgrade_name] = (
                upgrades.get(upgrade_name, 0) + 1
            )

            self.datadriver.users_df.at[self.author_id, "upgrades"] = upgrades # type: ignore

            self.datadriver.save_user(self.author_id)

        finally:
            self.update_view()
            await interaction.response.edit_message(view=self)