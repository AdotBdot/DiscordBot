import discord

class Card():
    def __init__(self, name="None"):
        self.name = name
        self.description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
        self.bundle = None
        self.collection = None
        self.rarity = "Common"
        self.image_url = "https://i.imgur.com/izgPuO1.jpeg"

    def to_embed(self):
        embed = discord.Embed()
        embed.title = self.name
        embed.description = f"**Description:** {self.description}\n**Bundle:** {self.bundle}\n**Collection:** {self.collection}\n**Rarity:** {self.rarity}"
        embed.set_image(url=self.image_url)
        return embed