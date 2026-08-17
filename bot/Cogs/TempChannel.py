import logging

import discord
from discord import app_commands
from discord.ext import commands

from bot.Utils.DataDriver import DataDriver

class TempChannel(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver: DataDriver = datadriver

        self.logger = logging.getLogger("TempChannel")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        
        if not self.logger.handlers:
            self.logger.addHandler(bot.logs_handler)
            self.logger.addHandler(bot.file_handler)

        self.create_channel_id = 806164430449672222
        self.category_id = 787000243547537439
        self.temp_channels: set[int] = set()

    def get_voice_overwrites(self, guild: discord.Guild, member_id: int) -> dict:
        member = guild.get_member(member_id)

        if member is None:
            raise ValueError(f"Member: {member_id} not found")

        return {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=True,
                connect=True,
                speak=True,
                use_voice_activation=True,
                stream=True
            ),
            member: discord.PermissionOverwrite(
                manage_channels=True,
            )
        }

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if after.channel is not None and after.channel.id == self.datadriver.config["create_channel_id"]:
            guild = member.guild
            category = guild.get_channel(self.datadriver.config["voice_category_id"])

            if not isinstance(category, discord.CategoryChannel):
                return

            overwrites = self.get_voice_overwrites(guild=member.guild, member_id=member.id)

            channel = await guild.create_voice_channel(
                name = f"🔶┋{member.display_name}", 
                category=category, 
                overwrites=overwrites,
                bitrate=96000, 
                reason=f"Temporary voice channel for {member}")
            self.temp_channels.add(channel.id)

            self.logger.info(f"Created temp voice channel: '{channel.name}'")

            try:
                await member.move_to(channel)
            except discord.HTTPException:
                await channel.delete(reason="Failed to move member")
                self.temp_channels.discard(channel.id)
                return

        if before.channel is not None and before.channel.id in self.temp_channels:
            channel = before.channel

            if len(channel.members) == 0:
                await channel.delete(reason="Temporary voice channel is empty")
                self.temp_channels.discard(channel.id)
                self.logger.info(f"Deleted temp voice channel: '{channel.name}'")

# Setup Cog
async def setup(bot):
    await bot.add_cog(TempChannel(bot, bot.datadriver))