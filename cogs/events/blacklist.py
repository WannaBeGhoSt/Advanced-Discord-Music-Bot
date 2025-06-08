"""Blacklist and Global Cooldown System made by GhoSty

This code is an Advanced Discord Music Bot using Wavelink and Discord.py.
Made by Ghosty || @ghostyjija
Feel free to skid it and use it as you want.

Support Server ( Async Development ): https://discord.gg/SyMJymrV8x
GitHub: https://github.com/WannaBeGhoSt
"""


import discord
from discord.ext import commands
import json
import os
import asyncio
from collections import defaultdict

from ghostyconfig import Ghostyname, Ghostycolor, Ghostyemojis


class Blacklist(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.spam_cd_mapping = commands.CooldownMapping.from_cooldown(5, 5, commands.BucketType.member)
        self.spam_command_mapping = commands.CooldownMapping.from_cooldown(6, 10, commands.BucketType.member)
        self.global_cd_mapping = commands.CooldownMapping.from_cooldown(1, 1.5, commands.BucketType.member)
        self.blacklist_file = "blacklist.json"
        self.blacklist = set()
        self.embed_cooldowns = defaultdict(lambda: 0)
        self.embed_cooldown_seconds = 10
        self.save_lock = asyncio.Lock()
        self.LoadBlsGhosty()

    def LoadBlsGhosty(self):
        if os.path.exists(self.blacklist_file):
            with open(self.blacklist_file, 'r') as f:
                self.blacklist = set(json.load(f))
        else:
            self.SaveBlsGhosty()

    def SaveBlsGhosty(self):
        with open(self.blacklist_file, 'w') as f:
            json.dump(list(self.blacklist), f, indent=4)

    async def adduserghostybl(self, user_id):
        if user_id not in self.blacklist:
            self.blacklist.add(user_id)
            async with self.save_lock:
                self.SaveBlsGhosty()

    def remuserghostybl(self, user_id):
        if user_id in self.blacklist:
            self.blacklist.remove(user_id)
            self.SaveBlsGhosty()

    def alrisblacklisghostyal(self, user_id):
        return user_id in self.blacklist

    @commands.command(name="blacklistremove")
    @commands.is_owner()
    async def removefromblacklist(self, ctx, user: discord.User):
        if user.id not in self.blacklist:
            await ctx.send(f"{user.mention} is not in the blacklist.")
        else:
            self.remuserghostybl(user.id)
            await ctx.send(f"Removed {user.mention} from the blacklist.")

    @commands.command(name="blacklist")
    @commands.is_owner()
    async def listblacklisted(self, ctx):
        if not self.blacklist:
            await ctx.send("No users are currently blacklisted.")
        else:
            blacklisted_users = "\n".join(
                [f"{idx + 1}. <@{user_id}>" for idx, user_id in enumerate(self.blacklist)]
            )
            embed = discord.Embed(
                title="Blacklisted Users",
                description=blacklisted_users,
                color=Ghostycolor
            )
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        if not hasattr(self.client, "_blacklist_check_registered"):
            self.client.add_check(self.blacklist_check)
            self.client.add_check(self.glcghostycdcheck)
            self.client._blacklist_check_registered = True

    async def blacklist_check(self, ctx):
        return ctx.author.id not in self.blacklist

    async def glcghostycdcheck(self, ctx):
        bucket = self.global_cd_mapping.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CheckFailure("Global cooldown active")
        return True

    async def mightghostyblembsend(self, user, channel, reason: str):
        now = discord.utils.utcnow().timestamp()
        last_sent = self.embed_cooldowns[user.id]
        if now - last_sent >= self.embed_cooldown_seconds:
            self.embed_cooldowns[user.id] = now
            embed = discord.Embed(
                description=f"**Successfully Blacklisted {user.mention} {reason}**",
                color=Ghostycolor
            )
            embed.set_footer(text="GhoSty | Blacklist")
            embed.set_thumbnail(url=self.client.user.display_avatar.url)
            try:
                await channel.send(embed=embed)
            except discord.Forbidden:
                pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        bucket = self.spam_cd_mapping.get_bucket(message)
        retry = bucket.update_rate_limit()

        if retry and message.content in [f'<@{self.client.user.id}>', f'<@!{self.client.user.id}>']:
            await self.adduserghostybl(message.author.id)
            await self.mightghostyblembsend(message.author, message.channel, "for spam mentioning me")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        if self.alrisblacklisghostyal(ctx.author.id):
            return

        bucket = self.spam_command_mapping.get_bucket(ctx.message)
        retry = bucket.update_rate_limit()

        if retry:
            await self.adduserghostybl(ctx.author.id)
            await self.mightghostyblembsend(ctx.author, ctx.channel, "for spamming my commands")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, (commands.CommandNotFound, commands.CheckFailure)):
            return
        print(f"Error: {error}")

async def setup(client):
    await client.add_cog(Blacklist(client))
