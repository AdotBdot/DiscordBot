import asyncio
from datetime import datetime, timedelta
import logging
import random
from typing import Callable, Awaitable, Any

import discord
from discord.ext import commands, tasks
from discord import app_commands

from bot.Utils.DataDriver import DataDriver

class EventManager:
    def __init__(self):

        self.events: dict[str, Callable[[discord.Message], Awaitable[None]]]
        self.active_events: set[int] = set()

    def register_event(self, event_name: str, event: Callable[[discord.Message], Awaitable[None]]) -> None:
        if event_name in self.events:
            return
        
        self.events[event_name] = event

    async def trigger(self, event_name: str, message: discord.Message) -> None:
        func = self.events.get(event_name)
        if func is None:
            return

        asyncio.create_task(func(message)) # type: ignore

class Events(commands.Cog):
    def __init__(self, bot, datadriver: DataDriver):
        self.bot = bot
        self.datadriver = datadriver

        self.logger = logging.getLogger("Events")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        
        if not self.logger.handlers:
            self.logger.addHandler(bot.logs_handler)
            self.logger.addHandler(bot.file_handler)

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

                    user_upgrades = self.datadriver.get_user_upgrades(user_id)
                    
                    if self.voice_time[user_id] % 10 == 0:
                        if random.random() <= 0.15 + user_upgrades["drop_rate"]/100:
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

    # ==========================
    # RANDOM EVENTS
    # ==========================

    # FIX: Overpowered as fuck
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Checks
        if message.author.bot:
            return

        user_id = message.author.id

        if not self.datadriver.user_exist(user_id):
            return

        # Fetch user upgrades
        user_upgrades = self.datadriver.get_user_upgrades(user_id)

        # Event chance
        if random.random() > 0.01 + user_upgrades["luck"]/100:
            return

        # Add reaction
        emoji = '🗿'

        try:
            await message.add_reaction(emoji)
        except discord.HTTPException:
            return

        # Timeout check
        def check(reaction_event: discord.Reaction, user: discord.User | discord.Member):
            return (user.id == user_id and reaction_event.message.id == message.id and str(reaction_event.emoji) == emoji)

        try:
            await self.bot.wait_for("reaction_add", timeout=10, check=check)
        except asyncio.TimeoutError:
            return

        # Give rewards to user
        multiplier = int(1 + user_upgrades["luck"]/5)
        reward_cash = random.randint(250*multiplier, 500*multiplier)

        user_cash = self.datadriver.get_user_cash(user_id)

        self.datadriver.set_user_cash(user_id, user_cash + reward_cash)

        # Logs
        self.logger.info(f"{user_id} claimed moiai event")

        # UI
        await message.channel.send(f"🗿 {message.author.mention} you've received {reward_cash} 🥥 🗿")

# Setup Cog
async def setup(bot):
    await bot.add_cog(Events(bot, bot.datadriver))