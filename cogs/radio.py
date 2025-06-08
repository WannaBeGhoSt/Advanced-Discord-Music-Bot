"""
This code is an Advanced Discord Music Bot using Wavelink and Discord.py.
Made by Ghosty || @ghostyjija
Feel free to skid it and use it as you want.

Support Server ( Async Development ): https://discord.gg/SyMJymrV8x
GitHub: https://github.com/WannaBeGhoSt
"""

import discord
import wavelink
from typing import cast
from discord.ext import commands
from ghostyconfig import Ghostyname, Ghostycolor, Ghostyemojis

GhostyRadChannels = {
    "All India Radio": "http://air.pc.cdn.bitgravity.com/air/live/pbaudio001/playlist.m3u8",
    "Radio Paradise": "http://stream-uk1.radioparadise.com/mp3-128",
    "NPR News": "https://npr-ice.streamguys1.com/live.mp3",
    "Classic FM": "https://media-ssl.musicradio.com/ClassicFMMP3",
}


class AsyncDevelopmentGhostyRadSel(discord.ui.Select):
    def __init__(self, vc: discord.VoiceClient):
        self.vc = vc
        options = [
            discord.SelectOption(label=name, value=url)
            for name, url in GhostyRadChannels.items()
        ]
        super().__init__(
            placeholder="Choose a radio station...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        label = [name for name, url in GhostyRadChannels.items() if url == selected][0]

        source = discord.FFmpegPCMAudio(
            selected,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-vn"
        )

    
        if isinstance(self.vc, discord.VoiceClient):
            if self.vc.is_playing():
                self.vc.stop()
            self.vc.play(source)
        else:
            await interaction.response.send_message(
                f"-# {Ghostyemojis.get('error')} | Radio streaming only supported with native discord.VoiceClient.",
                ephemeral=True
            )
            return
        
        radghostyemb = discord.Embed(
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Now streaming **{label}**.",
            color=Ghostycolor
        )
        await interaction.response.send_message(embed=radghostyemb, ephemeral=False)


class AsyncDevelopmentGhostyRadView(discord.ui.View):
    def __init__(self, vc: discord.VoiceClient):
        super().__init__(timeout=None)
        self.add_item(AsyncDevelopmentGhostyRadSel(vc))


class Radio(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def checkchannelghostyok(self, ctx: commands.Context) -> bool:
        if not ctx.guild:
            return False

        ghostyplayervc = ctx.guild.voice_client
        ghostyuservc = ctx.author.voice.channel if ctx.author.voice else None

        if ghostyplayervc:
            if not ghostyuservc or ghostyplayervc.channel != ghostyuservc:
                embed = discord.Embed(
                    description=f"-# {Ghostyemojis.get('error')} | You must be in {ghostyplayervc.channel.mention} to use this command.",
                    color=Ghostycolor
                )
                await ctx.send(embed=embed)
                return False
        else:
            if not ghostyuservc:
                embed = discord.Embed(
                    description=f"-# {Ghostyemojis.get('error')} | You need to join a voice channel to use this command.",
                    color=Ghostycolor
                )
                await ctx.send(embed=embed)
                return False

        return True

    async def ghostyplaycheck(self, ctx: commands.Context) -> bool:
        if not ctx.guild:
            return False

        vc = ctx.voice_client

        if isinstance(vc, wavelink.Player):
            if vc.playing:
                embed = discord.Embed(
                    description=f"-# {Ghostyemojis['error']} | I'm already playing something via music player. Use command `?disconnect` to stop it.",
                    color=Ghostycolor
                )
                await ctx.send(embed=embed)
                return False

        return True

    @commands.command()
    async def radio(self, ctx: commands.Context):
        """Play a radio station in your voice channel."""
        if not await self.checkchannelghostyok(ctx):
            return
        
        if not await self.ghostyplaycheck(ctx):
            return

        vc = ctx.voice_client
        wavelink_player = None
        if vc:
        
            if isinstance(vc, wavelink.Player):
                wavelink_player = vc
            else:
            
                pass

    
        if wavelink_player and wavelink_player.is_playing():
            await wavelink_player.stop()

        if not vc or not isinstance(vc, discord.VoiceClient):
        
            vc = await ctx.author.voice.channel.connect(cls=discord.VoiceClient)

        view = AsyncDevelopmentGhostyRadView(vc)
        embed = discord.Embed(
            description=f"-# {Ghostyemojis.get('check')} | Choose a radio station to stream.",
            color=Ghostycolor
        )
        await ctx.send(embed=embed, view=view)



async def setup(bot):
    await bot.add_cog(Radio(bot))
