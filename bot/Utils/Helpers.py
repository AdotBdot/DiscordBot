from bot.Utils.Enums import RARITY_ORDER

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