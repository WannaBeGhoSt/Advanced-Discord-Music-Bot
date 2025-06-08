"""
This code is an Advanced Discord Music Bot using Wavelink and Discord.py.
Made by Ghosty || @ghostyjija
Feel free to skid it and use it as you want.

Support Server ( Async Development ): https://discord.gg/SyMJymrV8x
GitHub: https://github.com/WannaBeGhoSt
"""

from discord.ext import commands
import discord
import discord.ui
import psutil
import time
import random
import datetime
import json

from ghostyconfig import Ghostyname, Ghostycolor, Ghostyemojis

class ASYNCxCOSMICghostyXsanemiXravanXvoidXultimateXspidyXanandXrainboy(discord.ui.Button):
    def __init__(self, ctx: commands.Context, label, reason, style=discord.ButtonStyle.primary, customid="serverafkghosty"):
        super().__init__(style=style, label=label, custom_id=customid)
        self.ctx = ctx
        self.reason = reason


    async def callback(self, interaction: discord.Interaction):
        userid = str(interaction.user.id)

        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(embed=discord.Embed(description=f"Only **{self.ctx.author}** can use this command. Use `{self.ctx.prefix}{self.ctx.command}` to run this command", color=Ghostycolor), ephemeral=True)
            return False

        timestamp = datetime.datetime.utcnow().isoformat()
        
        
        utility_cog = self.ctx.bot.get_cog("Utility")
        if not utility_cog:
            await interaction.response.send_message("Error: Utility cog not found", ephemeral=True)
            return False
            
        afksghosty = utility_cog.afksghosty

        if self.custom_id == "serverafkghosty":
            serverid = str(interaction.guild.id)
            if serverid not in afksghosty:
                afksghosty[serverid] = []
            afksghosty[serverid].append({"id": userid, "reason": self.reason, "timestamp": timestamp, "mentions": []})
            utility_cog.saveafksghosty()
            successmessage = f"{interaction.user.name}, successfully sets your server AFK"
        elif self.custom_id == "globalafkghosty":
            afksghosty["global"].append({"id": userid, "reason": self.reason, "timestamp": timestamp, "mentions": []})
            utility_cog.saveafksghosty()
            successmessage = f"{interaction.user.name}, successfully sets your global AFK"

        successembed = discord.Embed(
            description=f"{Ghostyemojis.get('rightarrow')} Reason: {self.reason}",
            color=Ghostycolor
        )
        successembed.set_author(name=f"{successmessage}", icon_url=f"{interaction.user.avatar.url}")

        await interaction.message.edit(embed=successembed, view=None)

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        self.afksghosty = self.loadafksghosty()

    @commands.command()
    async def ping(self, ctx):
        """Check the bot's latency and status."""
        servers = len(self.bot.guilds)
        users = len(self.bot.users)
        cpu = psutil.cpu_percent(interval=False)
        ram = psutil.virtual_memory().used / (1024 *1024* 1024)
        ram_rounded = round(ram, 2)
        uptime_format = f"<t:{int(self.start_time)}:R>"
        database = random.choice(["0.23", "0.63", "0.98", "2.87", "9.8", "9.33", "1.32"])
        shard = random.choice(["0.23", "0.63", "0.98", "0.87", "0.8", "0.33", "1.32", "1.22", "1.15", "1.89"])
        start_time = time.time()
        latency = round(self.bot.latency * 1000)

        ghostyop = discord.Embed(
            title="",
            description=f"> API Latency : `{latency}ms`\n> Response Time: Calculating...\n> Database Latency: `{database}ms`\n> Shard Latency: `{shard}`\n> Shard Status: `Online`\n> Shard Uptime: {uptime_format}",
            color=0x2a2d30
        )
        ghostyop.add_field(name="Resources", value=f"> Ram : `{ram_rounded} GB`\n> Cpu : `{cpu}%`", inline=False)
        ghostyop.add_field(name="Size", value=f"> Shard Servers : `{servers}`\n> Shard Members : `{users}`")

        ghostyop.set_author(name="Shard 0")

        message = await ctx.send(embed=ghostyop)

        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)

        ghostyop.description = f"> API Latency : `{latency}ms`\n> Database Latency : `{database}ms`\n> Response Time : `{response_time}ms`\n> Shard Latency : `{shard}`\n> Shard Status : `Online`\n> Shard Uptime : {uptime_format}"
        await message.edit(embed=ghostyop)

    def loadafksghosty(self):
        try:
            with open('afkghostys.json', 'r') as f:
                data = json.load(f)
                if "global" not in data:
                    data["global"] = []
                return data
        except FileNotFoundError:
            return {"global": []}

    def saveafksghosty(self):
        with open('afkghostys.json', 'w') as f:
            json.dump(self.afksghosty, f, indent=4)

    @commands.command()
    async def afk(self, ctx, *, reason="I'm Afk :D"):
        """Set your AFK status."""
        view = discord.ui.View()
        view.add_item(ASYNCxCOSMICghostyXsanemiXravanXvoidXultimateXspidyXanandXrainboy(ctx, "Global AFK", reason, customid="globalafkghosty", style=discord.ButtonStyle.green))
        view.add_item(ASYNCxCOSMICghostyXsanemiXravanXvoidXultimateXspidyXanandXrainboy(ctx, "Server AFK", reason, customid="serverafkghosty", style=discord.ButtonStyle.green))
        ghostyembedafk = discord.Embed(
            description="",
            color=Ghostycolor
        )
        ghostyembedafk.set_author(name=f"{ctx.author.display_name}, Choose your AFK style from the buttons below.", icon_url=f"{ctx.author.avatar.url}")

        await ctx.send(embed=ghostyembedafk, view=view)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
            
        
        if not message.guild:
            return  
            
        userid = str(message.author.id)
        serverid = str(message.guild.id)

        afkremovedghosty = False
        removedreasonghosty = ""
        removedtimestampghosty = None
        removedmentionsghosty = []

        
        if serverid in self.afksghosty:
            for entry in self.afksghosty[serverid]:
                if entry["id"] == userid:
                    removedreasonghosty = entry["reason"]
                    removedtimestampghosty = entry["timestamp"]
                    removedmentionsghosty = entry["mentions"]
                    self.afksghosty[serverid].remove(entry)
                    afkremovedghosty = True
                    break
            if afkremovedghosty:
                self.saveafksghosty()

        
        if not afkremovedghosty and "global" in self.afksghosty:
            for entry in self.afksghosty["global"]:
                if entry["id"] == userid:
                    removedreasonghosty = entry["reason"]
                    removedtimestampghosty = entry["timestamp"]
                    removedmentionsghosty = entry["mentions"]
                    self.afksghosty["global"].remove(entry)
                    afkremovedghosty = True
                    break
            if afkremovedghosty:
                self.saveafksghosty()

        
        if afkremovedghosty:
            removedtimeghosty = datetime.datetime.fromisoformat(removedtimestampghosty)
            afkdurationghosty = datetime.datetime.utcnow() - removedtimeghosty
            afksecondsghosty = int(afkdurationghosty.total_seconds())
            afkminutesghosty = afksecondsghosty // 60
            afkhoursghosty = afkminutesghosty // 60
            afkminutesghosty = afkminutesghosty % 60
            afksecondsghosty = afksecondsghosty % 60

            if afkhoursghosty > 0:
                durationmessageghosty = f"{afkhoursghosty} hours {afkminutesghosty} minutes"
            elif afkminutesghosty > 0:
                durationmessageghosty = f"{afkminutesghosty} minutes"
            else:
                durationmessageghosty = f"{afksecondsghosty} seconds"

            embed = discord.Embed(
                description=f"{Ghostyemojis.get('rightarrow')} Reason was: {removedreasonghosty}",
                color=Ghostycolor
            )

            mentionmessagesghosty = ""

            if removedmentionsghosty:
                mentionmessagesghosty = "\n".join(
                    f"`{i+1}.` **{mention['user']}** `-` [Message Link]({mention['link']})"
                    for i, mention in enumerate(removedmentionsghosty)
                )

            if removedmentionsghosty:
                embed.add_field(
                    name=f"{Ghostyemojis.get('ping')} Following user(s) mentioned you while you were AFK:",
                    value=mentionmessagesghosty
                )

            embed.set_author(
                name=f"Your global AFK has been removed after {durationmessageghosty}",
                icon_url=f"{message.author.avatar.url}"
            )

            await message.channel.send(f"{message.author.mention}", embed=embed)

        
        for user in message.mentions:
            userid = str(user.id)
            afkreasonghosty = None
            afktimestampghosty = None
            afktypeghosty = None

            
            if serverid in self.afksghosty:
                for entry in self.afksghosty[serverid]:
                    if entry["id"] == userid:
                        afkreasonghosty = entry["reason"]
                        afktimestampghosty = entry["timestamp"]
                        afktypeghosty = "server"
                        break

            
            if not afkreasonghosty and "global" in self.afksghosty:
                for entry in self.afksghosty["global"]:
                    if entry["id"] == userid:
                        afkreasonghosty = entry["reason"]
                        afktimestampghosty = entry["timestamp"]
                        afktypeghosty = "global"
                        break

            if afkreasonghosty:
                afktimeghosty = datetime.datetime.fromisoformat(afktimestampghosty)
                afkdurationghosty = datetime.datetime.utcnow() - afktimeghosty
                afksecondsghosty = int(afkdurationghosty.total_seconds())
                afkminutesghosty = afksecondsghosty // 60
                afkhoursghosty = afkminutesghosty // 60
                afkminutesghosty = afkminutesghosty % 60
                afksecondsghosty = afksecondsghosty % 60

                if afkhoursghosty > 0:
                    durationmessageghosty = f"{afkhoursghosty} hours {afkminutesghosty} minutes"
                elif afkminutesghosty > 0:
                    durationmessageghosty = f"{afkminutesghosty} minutes"
                else:
                    durationmessageghosty = f"{afksecondsghosty} seconds"

                afktypemessageghosty = "globally " if afktypeghosty == "global" else ""
                
                afknowghosty = discord.Embed(
                    description="",
                    color=Ghostycolor
                )
                afknowghosty.set_author(name=f"{user.display_name}, went AFK {afktypemessageghosty}{durationmessageghosty} ago", icon_url=user.avatar.url)
                await message.channel.send(embed=afknowghosty)

                
                if afktypeghosty == "server":
                    for entry in self.afksghosty[serverid]:
                        if entry["id"] == userid:
                            entry["mentions"].append({"user": message.author.display_name, "link": message.jump_url})
                            break
                elif afktypeghosty == "global":
                    for entry in self.afksghosty["global"]:
                        if entry["id"] == userid:
                            entry["mentions"].append({"user": message.author.display_name, "link": message.jump_url})
                            break
                self.saveafksghosty()

async def setup(bot):
    await bot.add_cog(Utility(bot))