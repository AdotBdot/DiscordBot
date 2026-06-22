from typing import Optional

import discord

from bot.Utils.DataDriver import DataDriver
from bot.Utils.Enums import UPGRADES_INFO

class UpgradeButton(discord.ui.Button):
    def __init__(self, upgrade_name: str, view: UpgradesView, label: str="Upgrade", style=discord.ButtonStyle.primary):
        super().__init__(label=label, style=style)

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
        return self.datadriver.users.at[self.author_id, "upgrades"] or {} # type: ignore
    
    def get_cash(self) -> int:
        return self.datadriver.users.at[self.author_id, "cash"] or 0 # type: ignore

    def get_melones(self) -> int:
        return self.datadriver.users.at[self.author_id, "melons"] or 0 # type: ignore

    def update_view(self):
        self.clear_items()

        # Header
        if self.header:
            self.add_item(self.header)

        user_cash = self.get_cash()

        # Content
        container = discord.ui.Container()
        upgrades = self.get_upgrades()

        for name, level in upgrades.items():
            cost = UPGRADES_INFO[name]["cost"]
            affordable = user_cash >= cost

            section = discord.ui.Section(
                discord.ui.TextDisplay(content=f"**{UPGRADES_INFO[name]["display_name"]}**: {level}\n{UPGRADES_INFO[name]["description"]}"),
                accessory=UpgradeButton(
                    upgrade_name=name,
                    view=self,
                    label=f"{UPGRADES_INFO[name]["cost"]}🥥",
                    style=discord.ButtonStyle.success if affordable else discord.ButtonStyle.primary
                )
            )

            section.accessory.disabled = not affordable # type: ignore

            container.add_item(section)

        self.add_item(container)

    async def upgrade(self, interaction: discord.Interaction, upgrade_name: str):
        try:
            cost = UPGRADES_INFO[upgrade_name]["cost"]
            user_cash = self.get_cash()

            self.datadriver.users.at[self.author_id, "cash"] = user_cash - cost

            upgrades = self.get_upgrades()
            upgrades[upgrade_name] = (
                upgrades.get(upgrade_name, 0) + 1
            )

            self.datadriver.users.at[self.author_id, "upgrades"] = upgrades # type: ignore

            self.datadriver.mark_dirty(self.author_id)

        finally:
            self.update_view()
            await interaction.response.edit_message(view=self)