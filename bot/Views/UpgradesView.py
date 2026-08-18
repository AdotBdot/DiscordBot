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

    def update_view(self):
        self.clear_items()

        # Header
        if self.header:
            self.add_item(self.header)

        user_cash = self.datadriver.get_user_cash(self.author_id)
        user_melones = self.datadriver.get_user_melones(self.author_id)

        # Content
        container = discord.ui.Container()
        upgrades = self.datadriver.get_user_upgrades(self.author_id)

        for name, level in upgrades.items():
            cost = UPGRADES_INFO[name]["base_cost"] * upgrades[name]
            cost_melones = 1 if upgrades[name] >= 10 else 0

            locked = user_cash >= cost and user_melones >= cost_melones and level < UPGRADES_INFO[name]["max_level"]

            label = ""
            if level >= UPGRADES_INFO[name]["max_level"]:
                label = "Max"
            else:
                label = f"{cost}🥥 {cost_melones}🍉" if cost_melones > 0 else f"{cost}🥥"

            section = discord.ui.Section(
                discord.ui.TextDisplay(content=f"**{UPGRADES_INFO[name]["display_name"]}**: {level}\n{UPGRADES_INFO[name]["description"]}"),
                accessory=UpgradeButton(
                    upgrade_name=name,
                    view=self,
                    label=label,
                    style=discord.ButtonStyle.success if locked else discord.ButtonStyle.primary
                )
            )

            section.accessory.disabled = not locked # type: ignore

            container.add_item(section)

        self.add_item(container)

    async def upgrade(self, interaction: discord.Interaction, upgrade_name: str):
        try:
            upgrades = self.datadriver.get_user_upgrades(self.author_id)
            user_cash = self.datadriver.get_user_cash(self.author_id)
            user_melones = self.datadriver.get_user_melones(self.author_id)

            cost = UPGRADES_INFO[upgrade_name]["base_cost"] * upgrades[upgrade_name]
            cost_melones = 1 if upgrades[upgrade_name] >= 10 else 0

            self.datadriver.set_user_cash(self.author_id, user_cash - cost)
            self.datadriver.set_user_melones(self.author_id, user_melones - cost_melones)

            upgrades[upgrade_name] = (
                upgrades.get(upgrade_name, 0) + 1
            )

            self.datadriver.set_user_upgrades(self.author_id, upgrades)

        finally:
            self.update_view()
            await interaction.response.edit_message(view=self)