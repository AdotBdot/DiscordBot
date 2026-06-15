import discord
from discord import app_commands

def admin_only():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator
    
    return app_commands.check(predicate)

def owner_only():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.id == interaction.guild.owner_id
    
    return app_commands.check(predicate)