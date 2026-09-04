from collections import Counter
import random

import discord

from bot.bot import Bot

from bot.Utils.DataDriver import DataDriver
from bot.Utils.Enums import RARITIES, RARITY_ORDER

def chunk_dict(data: dict, size: int = 10):
    items = list(data.items())

    return [dict(items[i:i + size]) for i in range(0, len(items), size)]

def chunk_list(data: list, size: int = 10):
    return [data[i:i + size] for i in range(0, len(data), size)]

#TODO: Fix \n
def wrap_text(text: str, limit: int = 48) -> list[str]:
    words = text.split()
    
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + (1 if current_line else 0) > limit:
            lines.append(current_line)
            current_line = word
        else:
            if current_line:
                current_line += " "
            current_line += word

    if current_line:
        lines.append(current_line)

    return lines

def sort_list_by_key(list: list[dict], key: str, reversed: bool = False) -> list[dict]:
    if key == "rarity":
        list_sorted = sorted(list, key=lambda x: RARITY_ORDER[x[key]], reverse=reversed)
    else:
        list_sorted = sorted(list, key=lambda x: x[key], reverse=reversed)
    return list_sorted

def merge_roll_rarity(rarity: str) -> str:
    index = RARITIES.index(rarity)

    if index < len(RARITIES) - 1:
        return RARITIES[index + 1]
    
    return rarity

def merge_roll_collection(collections: list[str]) -> str:
    counter = Counter(collections)

    names = list(counter.keys())
    weigts = list(counter.values())

    return random.choices(names, weights=weigts, k=1)[0]

def merge_cards(datadriver: DataDriver, user_id: int, selected_cards: list[str]):
    selected_df = datadriver.get_cards_by_names(selected_cards)

    source_rarity = selected_df["rarity"].iat[0]
    target_rarity = merge_roll_rarity(source_rarity) # type: ignore

    collection = merge_roll_collection(selected_df["collection"].tolist())

    df = datadriver.cards.copy()

    pool = df[(df["rarity"] == target_rarity) & (df["collection"] == collection)]

    if pool.empty:
        return None
    
    return pool.sample(n=1).iloc[0]

async def confirm(bot: Bot, interaction: discord.Interaction, message: str, timeout: float=20.0) -> bool:
    await interaction.followup.send(content=f"{message} (y/n/yes/no)")

    def check(msg):
        return (
            msg.author.id == interaction.user.id 
            and msg.channel.id == interaction.channel_id
            and msg.content.lower() in ["y", "yes", "n", "no"]
            )
    
    try:
        response = await bot.wait_for("message", timeout=timeout, check=check)

    except TimeoutError:
        return False
    
    return response.content.lower() in ["y", "yes"]