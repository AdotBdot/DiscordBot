RARITY_COLOR = {
    "Common": 0xfdfefe,
    "Uncommon": 0x27ae60,
    "Rare": 0x2471a3,
    "Epic": 0x7d3c98,
    "Legendary": 0xf1c40f,
    "Mythic": 0xd35400,
    "Divine": 0x34d8eb
}

BASE_RARITY_WEIGHT = {
    "Common": 70000,
    "Uncommon": 20000,
    "Rare": 7000,
    "Epic": 2000,
    "Legendary": 800,
    "Mythic": 190,
    "Divine": 10
}

RARITY_FLOOR = {
    "Common": 5000,
    "Uncommon": 10000,
    "Rare": 10000,
    "Epic": 5000,
    "Legendary": 3000,
    "Mythic": 1000,
    "Divine": 500
}

RARITY_TRANSFER = {
    "Common": {
        "Uncommon": 0.40,
        "Rare": 0.30,
        "Epic": 0.15,
        "Legendary": 0.10,
        "Mythic": 0.04,
        "Divine": 0.01,
    },
    "Uncommon": {
        "Rare": 0.50,
        "Epic": 0.25,
        "Legendary": 0.15,
        "Mythic": 0.08,
        "Divine": 0.02,
    },
    "Rare": {
        "Epic": 0.60,
        "Legendary": 0.25,
        "Mythic": 0.10,
        "Divine": 0.05,
    },
    "Epic": {
        "Legendary": 0.60,
        "Mythic": 0.30,
        "Divine": 0.10,
    },
    "Legendary": {
        "Mythic": 0.70,
        "Divine": 0.30,
    },
    "Mythic": {
        "Divine": 1.00,
    }
}

RARITY_EMOJI = {
    "Common": "🪨",
    "Uncommon": "🍃",
    "Rare": "💎",
    "Epic": "🔮",
    "Legendary": "🔥",
    "Mythic": "🌌",
    "Divine": "🌟"
}

RARITY_ORDER = {
    "Common": 1,
    "Uncommon": 2,
    "Rare": 3,
    "Epic": 4,
    "Legendary": 5,
    "Mythic": 6,
    "Divine": 7
}

UPGRADES_INFO = {
    "luck": {
        "display_name": "Luck",
        "description": "Increases chance of getting higher rarity card.",
        "cost": 1000
    }
}