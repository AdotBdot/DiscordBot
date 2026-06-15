from bot.Utils.Enums import RARITY_COLOR, RARITY_EMOJI
import discord
from discord.ext import commands

class Card():
    def __init__(self, name="None", description="None", bundle="None", collection="None", rarity="Common", image_url="https://i.imgur.com/izgPuO1.jpeg"):
        self.name = name
        self.bundle = bundle
        self.collection = collection
        self.description = description
        self.rarity = rarity
        self.image_url = image_url

    @classmethod
    def from_json(cls, data:dict, bundle_name:str, collection_name:str):
        return cls(
            name = data["name"],
            bundle = bundle_name,
            collection = collection_name,
            rarity = data["rarity"],
            description = data["description"],
            image_url = data["image_url"]
        )

    def to_container(self):
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"{RARITY_EMOJI[self.rarity]} **{self.rarity}** {self.name} {RARITY_EMOJI[self.rarity]}"),
            discord.ui.TextDisplay(content=f"**Bundle:** {self.bundle}\n**Collection:** {self.collection}\n{self.description}"),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=self.image_url
                )
            ),
            accent_color=RARITY_COLOR[self.rarity]
        )

        return container