from collections import Counter
import random

from bot.Utils.DataDriver import DataDriver
from bot.Utils.Enums import RARITIES, RARITY_ORDER, BASE_RARITY_WEIGHT, RARITY_TRANSFER, RARITY_FLOOR

def chunk_dict(data: dict, size: int = 10):
    items = list(data.items())

    return [dict(items[i:i + size]) for i in range(0, len(items), size)]

def chunk_list(data: list, size: int = 10):
    return [data[i:i + size] for i in range(0, len(data), size)]

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

def get_rarity_weights(level: int) -> dict[str, int]:
    if level <= 1:
        return BASE_RARITY_WEIGHT.copy()
    
    weights = BASE_RARITY_WEIGHT.copy()

    shift_per_level = 4000

    for _ in range (level - 1):
        remaining_shift = shift_per_level

        for rarity, targets in RARITY_TRANSFER.items():
            available = weights[rarity] - RARITY_FLOOR[rarity]

            if available <= 0:
                continue

            transfer = min(available, remaining_shift)

            if transfer <= 0:
                break

            weights[rarity] -= transfer
            remaining_shift -= transfer

            distributed = 0

            for target, ratio in targets.items():
                amount = int(transfer * ratio)
                weights[target] += amount
                distributed += amount

            last_target = list(targets.keys())[-1]
            weights[last_target] += transfer - distributed

            if remaining_shift <= 0:
                break

        if sum(weights.values()) != sum(BASE_RARITY_WEIGHT.values()):
            diff = sum(BASE_RARITY_WEIGHT.values()) - sum(weights.values())
            weights["Divine"] += diff

    return weights

def merge_roll_rarity(rarities: list[str]) -> str:
    counter = Counter(rarities)

    chosen = random.choices(list(counter.keys()), weights=list(counter.values()), k=1)[0]

    index = RARITIES.index(chosen)

    if index < len(RARITIES) - 1:
        return RARITIES[index + 1]
    
    return chosen

def merge_roll_collection(collections: list[str]) -> str:
    counter = Counter(collections)

    names = list(counter.keys())
    weigts = list(counter.values())

    return random.choices(names, weights=weigts, k=1)[0]

def merge_cards(datadriver: DataDriver, user_id: int, selected_cards: list[str]):
    selected_df = datadriver.get_cards_by_names(selected_cards)

    rarity = merge_roll_rarity(selected_df["rarity"].tolist())
    collection = merge_roll_collection(selected_df["collection"].tolist())

    df = datadriver.cards.copy()

    pool = df[(df["rarity"] == rarity) & (df["collection"] == collection)]

    if pool.empty:
        return None
    
    return pool.sample(1).iloc[0]
