from typing import Any

import discord

from bot.Utils.DataDriver import DataDriver
from bot.Utils.Enums import RARITY_VALUE, RARITY_EMOJI

class BuyButton(discord.ui.Button):
    def __init__(self, view: ShopView, item_type: str, item_name: str, price_cash: int, price_melones: int, style=discord.ButtonStyle.success):
        super().__init__()

        self.shop_view = view
        self.item_name = item_name
        self.item_type = item_type
        self.price_cash = price_cash
        self.price_melones = price_melones

        self.label = f"{price_cash}🥥 {price_melones}🍉" if price_melones > 0 else f"{price_cash}🥥"

    async def callback(self, interaction: discord.Interaction) -> Any:
        await self.shop_view.buy(interaction, self.item_type, self.item_name, self.price_cash, self.price_melones)

class ShopView(discord.ui.LayoutView):
    def __init__(self, author_id: int, datadriver: DataDriver):
        super().__init__()

        self.author_id = author_id
        self.datadriver = datadriver
        self.current_shop = "shop"

        # Header
        self.header = discord.ui.Container(
            discord.ui.TextDisplay(content="## Shop")
        )

        # Action Row
        self.shop_btn = discord.ui.Button(
            label="Shop",
            style = discord.ButtonStyle.primary,
            custom_id="shop"
        )

        self.daily_btn = discord.ui.Button(
            label="Daily",
            style=discord.ButtonStyle.primary,
            custom_id="daily"
        )
        
        self.shop_btn.callback = self.shop_page
        self.daily_btn.callback = self.daily_page

        self.actions = discord.ui.ActionRow(self.shop_btn, self.daily_btn)

        self.update_view()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.author_id
    
    def update_view(self):
        self.clear_items()

        self.add_item(self.header)

        user_cash = self.datadriver.get_user_cash(self.author_id)
        user_melones = self.datadriver.get_user_melones(self.author_id)

        # Shop Page
        packs = self.datadriver.packs_cache
        shop_container = discord.ui.Container()

        for pack in packs:
            item_price_cash = 250
            item_price_melones = 0

            section = discord.ui.Section(
                discord.ui.TextDisplay(content=f"📦 **{pack}**"),
                accessory=BuyButton(
                    view=self,
                    item_type="pack",
                    item_name=pack,
                    price_cash=item_price_cash,
                    price_melones=item_price_melones
                )
            )

            section.accessory.disabled = user_cash < item_price_cash or user_melones < item_price_melones # type: ignore

            shop_container.add_item(section)

        # Daily Shop page
        daily_cards = self.datadriver.get_daily_cards()
        daily_cards_df = self.datadriver.get_cards_by_names(daily_cards)

        daily_container = discord.ui.Container(discord.ui.TextDisplay(content="## Daily Cards"))

        for _, row in daily_cards_df.iterrows():
            rarity = row["rarity"]

            item_price_cash = RARITY_VALUE[rarity]
            item_price_melones = 0

            section = discord.ui.Section(
                discord.ui.TextDisplay(content=f"{RARITY_EMOJI[rarity]} **{row.name}**"),
                accessory=BuyButton(
                    view=self,
                    item_type="card",
                    item_name=row.name, # type: ignore
                    price_cash=item_price_cash,
                    price_melones=item_price_melones
                )
            )

            section.accessory.disabled = user_cash < item_price_cash or user_melones < item_price_melones # type: ignore

            daily_container.add_item(section)

        daily_container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        daily_container.add_item(discord.ui.TextDisplay(content="## Daily Packs"))

        daily_packs = self.datadriver.get_daily_packs()

        for daily_pack in daily_packs:
            item_price_cash = 250
            item_price_melones = 0

            section = discord.ui.Section(
                discord.ui.TextDisplay(content=f"📦 **{daily_pack}**"),
                accessory=BuyButton(
                    view=self,
                    item_type="pack",
                    item_name=daily_pack, # type: ignore
                    price_cash=item_price_cash,
                    price_melones=item_price_melones
                )
            )

            section.accessory.disabled = user_cash < item_price_cash or user_melones < item_price_melones # type: ignore

            daily_container.add_item(section)

        if self.current_shop == "shop":
            self.add_item(shop_container)
        else:
            self.add_item(daily_container)

        self.shop_btn.disabled = self.current_shop == "shop"
        self.daily_btn.disabled = self.current_shop == "daily"

        self.add_item(self.actions)

    async def shop_page(self, interaction: discord.Interaction):
        self.current_shop = "shop"
        
        self.update_view()
        await interaction.response.edit_message(view=self)

    async def daily_page(self, interaction: discord.Interaction):
        self.current_shop = "daily"
        
        self.update_view()
        await interaction.response.edit_message(view=self)

    async def buy(self, interaction: discord.Interaction, item_type: str, item_name: str, item_price_cash: int, item_price_melones: int):
        user_cash = self.datadriver.get_user_cash(self.author_id)
        user_melones = self.datadriver.get_user_melones(self.author_id)

        try:
            if item_type == "pack":
                user_packs = self.datadriver.get_user_packs(self.author_id)
                user_packs.append(item_name)
                self.datadriver.set_user_packs(self.author_id, user_packs)
            elif item_type == "card":
                user_cards = self.datadriver.get_user_cards(self.author_id)
                user_cards.append(item_name)
                self.datadriver.set_user_cards(self.author_id, user_cards)

            self.datadriver.set_user_cash(self.author_id, user_cash - item_price_cash)
            self.datadriver.set_user_melones(self.author_id, user_melones - item_price_melones)
        finally:
            self.update_view()
            await interaction.response.edit_message(view=self)
