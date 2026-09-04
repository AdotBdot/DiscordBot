RARITIES = [
    "Common",
    "Uncommon",
    "Rare",
    "Epic",
    "Legendary",
    "Mythic",
    "Divine"
]

RARITY_COLOR = {
    "Common": 0xfdfefe,
    "Uncommon": 0x27ae60,
    "Rare": 0x2471a3,
    "Epic": 0x7d3c98,
    "Legendary": 0xf1c40f,
    "Mythic": 0xd35400,
    "Divine": 0x34d8eb
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

RARITY_VALUE = {
    "Common": 10,
    "Uncommon": 25,
    "Rare": 80,
    "Epic": 300,
    "Legendary": 1000,
    "Mythic": 5000,
    "Divine": 50000
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

RARITY_FLOOR = {
    "Common": 5000,
    "Uncommon": 10000,
    "Rare": 10000,
    "Epic": 5000,
    "Legendary": 3000,
    "Mythic": 1000,
    "Divine": 500
}

RARITY_WEIGHTS = {
    0: {
        "Common": 70000,
        "Uncommon": 20000,
        "Rare": 7000,
        "Epic": 2000,
        "Legendary": 800,
        "Mythic": 190,
        "Divine": 10,
    },

    1: {
        "Common": 66000,
        "Uncommon": 21000,
        "Rare": 8000,
        "Epic": 3000,
        "Legendary": 1200,
        "Mythic": 650,
        "Divine": 150,
    },

    2: {
        "Common": 62000,
        "Uncommon": 22000,
        "Rare": 9000,
        "Epic": 4000,
        "Legendary": 1600,
        "Mythic": 1000,
        "Divine": 400,
    },

    3: {
        "Common": 58000,
        "Uncommon": 22500,
        "Rare": 10000,
        "Epic": 5000,
        "Legendary": 2200,
        "Mythic": 1500,
        "Divine": 800,
    },

    4: {
        "Common": 54000,
        "Uncommon": 23000,
        "Rare": 11000,
        "Epic": 6000,
        "Legendary": 2800,
        "Mythic": 2000,
        "Divine": 1200,
    },

    5: {
        "Common": 50000,
        "Uncommon": 23500,
        "Rare": 12000,
        "Epic": 7000,
        "Legendary": 3500,
        "Mythic": 2500,
        "Divine": 1500,
    },

    6: {
        "Common": 46000,
        "Uncommon": 24000,
        "Rare": 13000,
        "Epic": 8000,
        "Legendary": 4200,
        "Mythic": 3000,
        "Divine": 1800,
    },

    7: {
        "Common": 42000,
        "Uncommon": 24500,
        "Rare": 14000,
        "Epic": 9000,
        "Legendary": 5000,
        "Mythic": 3500,
        "Divine": 2000,
    },

    8: {
        "Common": 38000,
        "Uncommon": 25000,
        "Rare": 15000,
        "Epic": 10000,
        "Legendary": 5800,
        "Mythic": 4000,
        "Divine": 2200,
    },

    9: {
        "Common": 34000,
        "Uncommon": 25500,
        "Rare": 16000,
        "Epic": 11000,
        "Legendary": 6500,
        "Mythic": 4500,
        "Divine": 2500,
    },

    10: {
        "Common": 30000,
        "Uncommon": 26000,
        "Rare": 17000,
        "Epic": 12000,
        "Legendary": 7500,
        "Mythic": 5000,
        "Divine": 2500,
    },
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

UPGRADES_INFO = {
    "luck": {
        "display_name": "Luck",
        "description": "Increases overall luck.",
        "base_cost": 1000,
        "max_level": 10
    },
    "drop_rate": {
        "display_name": "Drop Rate",
        "description": "Increases chance of getting a pack.",
        "base_cost": 1000,
        "max_level": 10
    },
    "pack_size": {
        "display_name": "Pack Size",
        "description": "Chance of getting more cards in a pack.",
        "base_cost": 1000,
        "max_level": 5
    }
}