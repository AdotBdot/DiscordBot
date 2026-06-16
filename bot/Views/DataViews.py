import discord
from discord.ext import commands

from bot.Utils.Enums import RARITY_COLOR, RARITY_EMOJI

def card_to_container(card: dict) -> discord.ui.Container:
    rarity = card["rarity"]
    container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"{RARITY_EMOJI[rarity]} **{rarity}** {card["name"]} {RARITY_EMOJI[rarity]}"),
            discord.ui.TextDisplay(content=f"**Bundle:** {card["bundle"]}\n**Collection:** {card["collection"]}\n**Tags**: {", ".join([tag for tag in card["tags"]])}\n{card["description"]}"),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(media=card["image_url"])
            ),
            accent_color=RARITY_COLOR[card["rarity"]]
        )
    
    return container

def user_to_container(user: dict, avatar_url: str, total_cards: int) -> discord.ui.Container:
    container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"**Collection Size**: {len(user["cards"])}\n**Completion**: {len(set(user["cards"]))}/{total_cards}"),
            discord.ui.TextDisplay(content=f"**Cocoses**: {user["cash"]} 🥥\n**Melones**: {user["melons"]} 🍉")
        )

    return container

def inv_to_container(user: dict, avatar_url: str) -> discord.ui.Container:
        packs = {}
        for pack_name in user["packs"]:
            packs[pack_name] = packs.get(pack_name, 0) + 1

        msg = ""

        for key, value in packs.items():
            msg = msg + f"**{key}**: {value}x\n"

        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Packs"),
            discord.ui.TextDisplay(content=msg)
        )

        return container