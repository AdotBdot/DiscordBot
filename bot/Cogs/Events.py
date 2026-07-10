from datetime import datetime, timedelta
import logging
import random

import discord
from discord.ext import commands, tasks
from discord import app_commands

from bot.Utils.DataDriver import DataDriver

class Events(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver = datadriver

        self.logger = logging.getLogger("Events")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.logger.addHandler(bot.logs_handler)

        self.voice_time = {}

        self.voice_rewards.start()
        self.daily_shop_checker.start()

    def cog_unload(self):
        self.voice_rewards.cancel()
        self.daily_shop_checker.cancel()

    # ==========================
    # VOICE TIME REWARDS
    # ==========================

    @tasks.loop(minutes=1)
    async def voice_rewards(self):
        guilds = self.bot.guilds

        for guild in guilds:
            for channel in guild.voice_channels:
                for member in channel.members:

                    if member.bot:
                        continue
                    
                    user_id = member.id

                    if not self.datadriver.user_exist(user_id):
                        continue

                    self.voice_time[user_id] = (self.voice_time.get(user_id, 0) + 1)

                    if self.voice_time[user_id] % 10 == 0:
                        if random.random() <= 0.20:
                            await self.give_random_pack(user_id)

    async def give_random_pack(self, user_id):
        pack = random.choice(self.datadriver.packs_cache)
        user_packs = self.datadriver.get_user_packs(user_id)
        user_packs.append(pack)
        self.datadriver.set_user_packs(user_id, user_packs)

        user = self.bot.get_user(user_id)

        if user:
            try:
                # Logs
                self.logger.info(f"Gave random pack: '{pack}' to {user_id}")

                await user.send(f"You received a random pack: **{pack}**")
            except discord.Forbidden:
                pass

    # ==========================
    # DAILIES
    # ==========================

    @tasks.loop(minutes=5)
    async def daily_shop_checker(self):
        now = datetime.now()
        last_refresh = self.datadriver.get_last_daily_refresh()

        if last_refresh is None:
            self.datadriver.refresh_daily()
            return
        
        if now - last_refresh >= timedelta(hours=24):
            self.datadriver.refresh_daily()
            return
        
        next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

        if now >= next_midnight:
            self.datadriver.refresh_daily()

# Setup Cog
async def setup(bot):
    await bot.add_cog(Events(bot, bot.datadriver))