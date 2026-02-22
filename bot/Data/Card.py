import discord

class Card():
    def __init__(self, name="None", description="None", bundle="None", collection="None", rarity="Common", image_url="https://i.imgur.com/izgPuO1.jpeg"):
        self.name = name
        self.description = description
        self.bundle = bundle
        self.collection = collection
        self.rarity = rarity
        self.image_url = image_url

    def to_embed(self):
        embed = discord.Embed()
        embed.title = self.name
        embed.description = f"**Bundle:** {self.bundle}\n**Collection:** {self.collection}\n**Rarity:** {self.rarity}\n**Description:** {self.description}"
        embed.set_image(url=self.image_url)
        return embed