"""
This code is an Advanced Discord Music Bot using Wavelink and Discord.py.
Made by Ghosty || @ghostyjija
Feel free to skid it and use it as you want.

Support Server ( Async Development ): https://discord.gg/SyMJymrV8x
GitHub: https://github.com/WannaBeGhoSt
"""

import discord
from discord.ext import commands
from ghostyconfig import Ghostyname, Ghostycolor, Ghostyemojis

class Ghostyview(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=180)  
        
        ghostyinvite = discord.ui.Button(
            label="Invite Me",
            url=f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands"  
        )
        self.add_item(ghostyinvite)

        ghostysupport = discord.ui.Button(
            label="Support Server",
            url="https://discord.gg/SyMJymrV8x"  
        )
        self.add_item(ghostysupport)
        
        ghostyvote = discord.ui.Button(
            label="Vote Me",
            url="https://discord.gg/SyMJymrV8x"  
        )
        self.add_item(ghostyvote)

class OnTag(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if message.content == f"<@{self.bot.user.id}>":
            current_prefix = "?"
            embed = discord.Embed(
                title="",
                description=f"{Ghostyemojis.get('love')} Hey {message.author.mention}, My prefix for this server is the following\n\n{Ghostyemojis.get('rightarrow')} For further help with the bot you can use the following commands\n\n**Prefix**\n- {current_prefix}help\n- {current_prefix}help `[command name]`\n\n**Mention**\n- {self.bot.user.mention} help\n- {self.bot.user.mention} help `[command name]`",
                color=Ghostycolor
            )
            embed.set_thumbnail(url=message.author.display_avatar.url if message.author else None)
            ghostyimgpath = "C:/Users/user2/Desktop/GhoSty Music Bot/assets/ghostyhaqwp.jpg"
            file = discord.File(ghostyimgpath, filename="ghostyhaqwp.jpg")
            embed.set_image(url="attachment://ghostyhaqwp.jpg")
            
            view = Ghostyview(self.bot)
            
            ghostytop = discord.AllowedMentions.none()
            await message.reply(embed=embed, file=file, view=view, allowed_mentions=ghostytop)

async def setup(bot):
    await bot.add_cog(OnTag(bot))