import discord
from discord.ext import commands

from bot.Utils.Enums import RARITY_COLOR, RARITY_EMOJI
from bot.Utils.Helpers import wrap_text

def card_to_container(card: dict) -> discord.ui.Container:
    rarity = card["rarity"]
    description = "\n".join(wrap_text("**Description**: " + card["description"]))

    tags = ""
    if card["tags"]:
        tags = ", ".join([tag for tag in card["tags"]])
    else: 
        tags = "None" 

    container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"## {card["name"]}"),
            discord.ui.TextDisplay(content=f"**Rarity**: {rarity} {RARITY_EMOJI[rarity]}\n**Bundle:** {card["bundle"]}\n**Collection:** {card["collection"]}\n**Tags**: {tags}"),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(media=card["image_url"])
            ),
            discord.ui.TextDisplay(content=description),
            accent_color=RARITY_COLOR[card["rarity"]]
        )
    
    return container

def user_to_container(user: dict, total_cards: int) -> discord.ui.Container:
    container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### Collection\n**Size**: {len(user["cards"])}\n**Completion**: {len(set(user["cards"]))}/{total_cards}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=f"### Currency\n**Cocoses**: {user["cash"]} 🥥\n**Melones**: {user["melons"]} 🍉")
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