"""
This code is an Advanced Discord Music Bot using Wavelink and Discord.py.
Made by Ghosty || @ghostyjija
Feel free to skid it and use it as you want.

Support Server ( Async Development ): https://discord.gg/SyMJymrV8x
GitHub: https://github.com/WannaBeGhoSt
"""

import discord
import wavelink
import asyncio
import aiohttp
import io

from discord.ext import commands
from typing import cast, Optional
from discord.ui import Select, View
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from ghostyconfig import Ghostyname, Ghostycolor, Ghostyemojis

Gghostygenres = {
    "phonk": "8LQP804v2cA",
    "hindi_romantic": "-2RAq5o5pwc",
    "hindi_sad": "8of5w7RgcTc",
    "english": "Acj_kh5IH-E",
    "viral": "ki0Ocze98U8"
}

class Dhitsghostydrop(discord.ui.Select):
    def __init__(self, bot, ctx, fetch_func):
        self.bot = bot
        self.ctx = ctx
        self.fetch_func = fetch_func
        self.player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        self.player.home = ctx.channel

        options = [
            discord.SelectOption(label="Phonk", value="phonk", description="Dark trap phonk hits"),
            discord.SelectOption(label="Hindi Romantic", value="hindi_romantic", description="Love & feels"),
            discord.SelectOption(label="Hindi Sad", value="hindi_sad", description="Breakup & sad vibes"),
            discord.SelectOption(label="English", value="english", description="Top English picks"),
            discord.SelectOption(label="Viral", value="viral", description="Internet trending songs")
        ]

        super().__init__(
            placeholder="Choose a genre",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        genreghostyvals = self.values[0]
        vid_id = Gghostygenres.get(genreghostyvals)
        if not vid_id:
            return await interaction.response.send_message("Invalid genre selected.", ephemeral=True)

        await interaction.response.defer()
        player: wavelink.Player = self.ctx.voice_client
        fetched_tracks = await self.fetch_func(vid_id)

        if not fetched_tracks:
            return await interaction.followup.send("Couldn't fetch any songs from YouTube.")

        added = 0
        first_track = None
        for data in fetched_tracks:
            track = await wavelink.Playable.search(data["url"], source="youtube")
            if isinstance(track, list) and track:
                track = track[0]
            if isinstance(track, wavelink.Playable):
                if not first_track and not player.playing:
                    first_track = track
                else:
                    player.queue.put(track)
                added += 1

        if first_track:
            await player.play(first_track)
        
        addedghostyemb = discord.Embed( 
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Added **{added}** `{genreghostyvals.replace('_', ' ').title()}` tracks to the queue",
            color=Ghostycolor
        )

        await interaction.followup.send(embed=addedghostyemb)

class Dhitsghostyview(discord.ui.View):
    def __init__(self, bot, ctx, fetch_func):
        super().__init__(timeout=60)
        self.add_item(Dhitsghostydrop(bot, ctx, fetch_func))

class Loopghostyselect(Select):
    def __init__(self, player: wavelink.Player, author_id: int):
        self.player = player
        self.author_id = author_id

        options = [
            discord.SelectOption(label="Track", description="Loop the current track", value="loop"),
            discord.SelectOption(label="Queue", description="Loop the whole queue", value="loop_all"),
            discord.SelectOption(label="Reset", description="Disable loop", value="normal")
        ]

        super().__init__(placeholder="Select loop mode", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You can't interact with this element.", ephemeral=True)
            return

        selected = self.values[0]
        new_mode = getattr(wavelink.QueueMode, selected)
        self.player.queue.mode = new_mode

        status_map = {
            wavelink.QueueMode.loop: "Looping **track**",
            wavelink.QueueMode.loop_all: "Looping **queue**",
            wavelink.QueueMode.normal: "Looping **disabled**"
        }

        embed = discord.Embed(
            title="",
            description=status_map[new_mode],
            color=Ghostycolor
        )
        await interaction.response.edit_message(embed=embed, view=self.view)


class Loopghostyview(View):
    def __init__(self, player: wavelink.Player, author_id: int):
        super().__init__(timeout=60)
        self.select = Loopghostyselect(player, author_id)
        self.add_item(self.select)

    async def on_timeout(self):
        self.select.disabled = True
        for item in self.children:
            item.disabled = True
        if hasattr(self, 'message'):
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass

class SimGhostyMenu(Select):
    def __init__(self, tracks, player, author_id):
        options = [
            discord.SelectOption(label=track['title'], value=track['identifier'])
            for track in tracks
        ]
        super().__init__(placeholder="Select tracks to add to queue", max_values=7, min_values=1, options=options)
        self.player = player
        self.author_id = author_id
        self.tracks_map = {track['identifier']: track for track in tracks}

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You cannot interact with this element.", ephemeral=True)
            return False
        return True

    async def callback(self, interaction: discord.Interaction):
        added_tracks = []
        for track_id in self.values:
            track_info = self.tracks_map.get(track_id)
            if not track_info:
                continue

            try:
                tracks: wavelink.Search = await wavelink.Playable.search(track_info['url'])
            except Exception as e:
                print(f"Error searching {track_info['url']}: {e}")
                continue

            if tracks:
                await self.player.queue.put_wait(tracks[0])
                added_tracks.append(track_info['title'])

        await interaction.response.send_message(
            f"Added {len(added_tracks)} track(s) to the queue:\n" + "\n".join(f"- {t}" for t in added_tracks),
            ephemeral=True
        )
        self.view.stop()



class ghostyqview(discord.ui.View):
    def __init__(self, ctx: commands.Context, player: wavelink.Player):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.player = player
        self.queue = player.queue.copy()
        self.current = player.current
        self.page = 0
        self.tracks_per_page = 5
        self.total_pages = max(1, (len(self.queue) + self.tracks_per_page - 1) // self.tracks_per_page)
        self.message: Optional[discord.Message] = None
        self.ghostyupdbuttons()

    def ghostyupdbuttons(self):
        self.previous_button.disabled = self.page == 0
        self.next_button.disabled = self.page >= self.total_pages - 1

    def ghostyformatph(self) -> discord.Embed:
        ghostyqueueembed = discord.Embed(
            title="",
            color=Ghostycolor
        )
        if self.current:
            ghostyqueueembed.add_field(name="Now Playing", value=f"[{self.current.title}]({self.current.uri})", inline=False)
        else:
            ghostyqueueembed.add_field(name="Now Playing", value="Nothing is playing.", inline=False)

        start = self.page * self.tracks_per_page
        end = start + self.tracks_per_page
        queuepageghostyolaf = self.queue[start:end]

        if queuepageghostyolaf:
            description = ""
            for idx, track in enumerate(queuepageghostyolaf, start=start + 1):
                line = f"{idx}. [{track.title}]({track.uri})\n"
        
                if len(description) + len(line) > 1024:
                    description += "...and more."
                    break
                description += line
            ghostyqueueembed.add_field(name="Up Next", value=description, inline=False)
        else:
            ghostyqueueembed.add_field(name="Up Next", value="The queue is empty.", inline=False)

        ghostyqueueembed.set_footer(text=f"Page {self.page + 1}/{self.total_pages}")
        return ghostyqueueembed

    @discord.ui.button(emoji=f"{Ghostyemojis.get('leftarrow')}", style=discord.ButtonStyle.gray)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("You can't interact with this button.", ephemeral=True)
            return
        self.page -= 1
        self.ghostyupdbuttons()
        await interaction.response.edit_message(embed=self.ghostyformatph(), view=self)

    @discord.ui.button(emoji=f"{Ghostyemojis.get('rightarrow')}", style=discord.ButtonStyle.gray)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("You can't interact with this button.", ephemeral=True)
            return
        self.page += 1
        self.ghostyupdbuttons()
        await interaction.response.edit_message(embed=self.ghostyformatph(), view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(view=self)
            
class Music(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    async def checkchannelghostyok(self, ctx: commands.Context) -> bool:
        if not ctx.guild:
           return False

        ghostyplayervc = ctx.guild.voice_client
        ghostyuservc = ctx.author.voice.channel if ctx.author.voice else None

        if ghostyplayervc:
            if not ghostyuservc or ghostyplayervc.channel != ghostyuservc:
                embed = discord.Embed(
                    title="",
                    description=f"-# {Ghostyemojis.get('error')} | You must be in {ghostyplayervc.channel.mention} to use this command.",
                    color=Ghostycolor
                )
                await ctx.send(embed=embed)
                return False
        else:
            if not ghostyuservc:
               embed = discord.Embed(
                    title="",
                    description=f"-# {Ghostyemojis.get('error')} | You need to join a voice channel to use this command.",
                    color=Ghostycolor
                )
               
               await ctx.send(embed=embed)
               return False

        return True

    async def ghostyplaycheck(self, ctx: commands.Context) -> bool:
        if not ctx.guild:
            return False

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        user_vc = ctx.author.voice.channel if ctx.author.voice else None

        if not player or not player.playing:
            if user_vc:
                embed = discord.Embed(
                    title="",
                    description=f"-# {Ghostyemojis['error']} | I'm not playing anything right now.",
                    color=Ghostycolor
                )
                await ctx.send(embed=embed)
            return False

        return True


    async def genmusiccardghosty(self, title: str, author: str, artwork_url: str, duration: str) -> discord.File:          
        title_font = ImageFont.truetype("arialbd.ttf", 44)
        subtitle_font = ImageFont.truetype("arial.ttf", 28)
        duration_font = ImageFont.truetype("arial.ttf", 24)
    
        
        width, height = 1280, 400
        
        
        async with aiohttp.ClientSession() as session:
            async with session.get(artwork_url) as resp:
                if resp.status != 200:
                    raise Exception("Failed to load artwork")
                data = io.BytesIO(await resp.read())
        
        artwork = Image.open(data).convert("RGB")
        
        
        bg = artwork.resize((width, height), Image.Resampling.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(40))
        
        
        bg = Image.blend(bg, Image.new("RGB", (width, height), (20, 20, 25)), 0.7)
        
        
        gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        gradient_draw = ImageDraw.Draw(gradient)
        for y in range(height):
            alpha = int(80 * (y / height))
            gradient_draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
        
        bg = bg.convert("RGBA")
        bg = Image.alpha_composite(bg, gradient)
        
        
        artwork_size = 320
        session = aiohttp.ClientSession()
        resp = await session.get(artwork_url)
        artwork_data = await resp.read()
        await session.close()
        
        artwork = Image.open(io.BytesIO(artwork_data))
        artwork = artwork.resize((artwork_size, artwork_size)).convert("RGBA")
        
        
        mask = Image.new("L", (artwork_size, artwork_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle((0, 0, artwork_size, artwork_size), radius=25, fill=255)
        artwork.putalpha(mask)
        
        
        artwork_x = width - artwork_size - 50
        artwork_y = (height - artwork_size) // 2
        
        
        bg.paste(artwork, (artwork_x, artwork_y), artwork)
        
        
        card = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        card_draw = ImageDraw.Draw(card)
        
        
        glass_left = 40
        glass_top = 40
        glass_right = artwork_x - 30  
        glass_bottom = height - 40
        
        
        card_draw.rounded_rectangle(
            [glass_left, glass_top, glass_right, glass_bottom],
            radius=35,
            fill=(255, 255, 255, 15)  
        )
        
        
        card_draw.rounded_rectangle(
            [glass_left, glass_top, glass_right, glass_bottom],
            radius=35,
            outline=(255, 255, 255, 40),
            width=1
        )
        
        
        bg = Image.alpha_composite(bg, card)
        draw = ImageDraw.Draw(bg)
        
        
        def truncate_text(text: str, font, max_width: int) -> str:
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            
            if text_width <= max_width:
                return text
            
            while len(text) > 0:
                test_text = text + "..."
                text_bbox = draw.textbbox((0, 0), test_text, font=font)
                if text_bbox[2] - text_bbox[0] <= max_width:
                    return test_text
                text = text[:-1]
            return "..."
        
        
        text_start_x = 80
        text_max_width = glass_right - text_start_x - 40
        
        
        truncated_title = truncate_text(title, title_font, text_max_width)
        draw.text((text_start_x, 90), truncated_title, font=title_font, fill=(255, 255, 255, 250))
        
        
        truncated_author = truncate_text(author, subtitle_font, text_max_width)
        draw.text((text_start_x, 150), truncated_author, font=subtitle_font, fill=(255, 255, 255, 180))
        
        
        draw.text((text_start_x, 280), f"Duration: {duration}", font=duration_font, fill=(255, 255, 255, 160))
        
        
        bar_x = text_start_x
        bar_y = 330
        bar_width = text_max_width
        bar_height = 4
        
        
        draw.rounded_rectangle(
            [bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
            radius=2,
            fill=(255, 255, 255, 50)
        )
        
        
        fill_width = int(bar_width * 0.15)
        draw.rounded_rectangle(
            [bar_x, bar_y, bar_x + fill_width, bar_y + bar_height],
            radius=2,
            fill=(255, 255, 255, 200)  
        )
        
        
        dot_radius = 8
        dot_x = bar_x + fill_width
        dot_y = bar_y + (bar_height // 2)
        
        
        draw.ellipse(
            [dot_x - dot_radius + 1, dot_y - dot_radius + 1, 
             dot_x + dot_radius + 1, dot_y + dot_radius + 1],
            fill=(0, 0, 0, 60)
        )
        
        
        draw.ellipse(
            [dot_x - dot_radius, dot_y - dot_radius, 
             dot_x + dot_radius, dot_y + dot_radius],
            fill=(255, 255, 255, 255)
        )
        
        
        bg = bg.convert("RGB")
        
        
        buffer = io.BytesIO()
        bg.save(buffer, format="PNG", quality=95)
        buffer.seek(0)
        return discord.File(fp=buffer, filename="ghostymusiccard.png")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
        player = payload.player
        original: wavelink.Playable | None = payload.original
        track: wavelink.Playable = payload.track
        
        if player.channel:
            status = f"{track.title} | GhoSty"
            await self.updvoicechannelghostystatus(player.channel.id, status)

        if not player or not track:
            return

        duration = f"{int(track.length // 60000)}:{int((track.length % 60000) // 1000):02d}"
        card_file = await self.genmusiccardghosty(track.title, track.author, track.artwork, duration)

        embed = discord.Embed(
            title="",
            description=f"-# **[{track.title}]({track.uri})** by {track.author}",
            color=Ghostycolor
        )
        if original and original.recommended:
            embed.description += f"\n\nThis track was recommended via {track.source}"
        embed.set_image(url="attachment://ghostymusiccard.png")
        await player.home.send(embed=embed, file=card_file)



    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        """Handle what happens when a track ends."""
        player: wavelink.Player | None = payload.player
        if not player or not player.guild:
            return

        guild_id = player.guild.id
        queue = player.queue
        track = payload.track

    
        if queue.mode == wavelink.QueueMode.loop:
            await player.play(track)
        
            if player.channel:
                await self.updvoicechannelghostystatus(player.channel.id, f"{track.title} | GhoSty")
            return

        elif queue.mode == wavelink.QueueMode.loop_all:
            queue.put(track)
            try:
                next_track = queue.get()
                await player.play(next_track)
            
                if player.channel:
                    await self.updvoicechannelghostystatus(player.channel.id, f"{next_track.title} | GhoSty")
            except Exception as e:
                if hasattr(player, 'home'):
                    await player.home.send("Error playing next track. Please disconnect and try again.")
            return

    
        if not queue.is_empty and not player.playing and not player.paused:
            try:
                next_track = queue.get()
                await player.play(next_track)
            
                if player.channel:
                    await self.updvoicechannelghostystatus(player.channel.id, f"{next_track.title} | GhoSty")
            except Exception as e:
                if hasattr(player, 'home'):
                    await player.home.send("Error playing next track. Please disconnect and try again.")
            return

  
        if not player.current and queue.is_empty and not player.autoplay:
            try:
   
                await self.updvoicechannelghostystatus(player.channel.id, "?play <query> | GhoSty")
                await self.start_inactivity_timer(guild_id, player)
            except Exception as e:
                print(f"Error handling empty queue state: {e}")





   # @commands.Cog.listener()
  #  async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        """Handle what happens when a track ends."""
        player: wavelink.Player | None = payload.player
        if not player or not player.guild:
            return

        guild_id = player.guild.id
        queue = player.queue
        track = payload.track


        if queue.mode == wavelink.QueueMode.loop:
  
            await player.play(track)
            return

        elif queue.mode == wavelink.QueueMode.loop_all:
     
            queue.put(track)
            try:
                next_track = queue.get()
                await player.play(next_track)
            except Exception as e:
                if hasattr(player, 'home'):
                    await player.home.send("Error playing next track. Please disconnect and try again.")
            return


        if not queue.is_empty and not player.playing and not player.paused:
            try:
                next_track = queue.get()
                await player.play(next_track)
            except Exception as e:
                if hasattr(player, 'home'):
                    await player.home.send("Error playing next track. Please disconnect and try again.")
            return
        
        if queue.is_empty and not player.autoplay:
            await self.start_inactivity_timer(guild_id, player)


    async def updvoicechannelghostystatus(self, channel_id: int, status: str) -> None:
        url = f"https://discord.com/api/v9/channels/{channel_id}/voice-status"
        headers = {
            "Authorization": f"Bot {self.bot.http.token}",
            "Content-Type": "application/json"
        }
        payload = {"status": status}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(url, json=payload, headers=headers) as response:
                    if response.status not in (200, 204):
                        print(f"Failed to update voice status: {response.status}")
        except Exception as e:
            print(f"Voice status update error: {e}")

    @commands.command(aliases=["P"])
    async def Play(self, ctx: commands.Context, *, query: str) -> None:
        """Play a song with the given query."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not ctx.guild:
           return

        vc = ctx.voice_client
    
    # Agar native discord.VoiceClient hai (jo radio ke liye hai)
        if isinstance(vc, discord.VoiceClient) and not isinstance(vc, wavelink.Player):
            embed = discord.Embed(
                description=f"-# {Ghostyemojis.get('error')} | Radio is currently streaming. Use `?disconnect` to stop it before playing music.",
                color=Ghostycolor
            )
            await ctx.send(embed=embed)
            return

    # Wavelink player ko cast karo
        player: wavelink.Player
        player = cast(wavelink.Player, vc)  # type: ignore

        if not player:
            try:
                player = await ctx.author.voice.channel.connect(cls=wavelink.Player)  # type: ignore
            except AttributeError:
                return
            except discord.ClientException:
                return

        player.autoplay = wavelink.AutoPlayMode.disabled

        if not hasattr(player, "home"):
            player.home = ctx.channel
        elif player.home != ctx.channel:
            return

        tracks: wavelink.Search = await wavelink.Playable.search(query, source="ytsearch")
        if not tracks:
            await ctx.send(f"{ctx.author.mention} - Could not find any tracks with that query. Please try again.")
            return

        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            await ctx.send(f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue.")
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            queuesghostyemb = discord.Embed(
                title="",
                description=f"-# {Ghostyemojis.get('check')} | Added **`{track.title}`** to the queue.",
                color=Ghostycolor
            )
        await ctx.send(embed=queuesghostyemb)

        if not player.playing:
            await player.play(player.queue.get())

    @commands.command()
    async def Skip(self, ctx: commands.Context) -> None:
        """Skip the current song."""
        if not await self.checkchannelghostyok(ctx):            
            return
        if not await self.ghostyplaycheck(ctx):
            return
    
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        await player.skip(force=True)
        skipghostyemb = discord.Embed(
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Skipped the current track.",
            color=Ghostycolor
        )
        await ctx.send(embed=skipghostyemb)


        try:
            if (player.autoplay == wavelink.AutoPlayMode.disabled 
                and not player.current 
                and player.queue.is_empty):
                if not player.current and player.queue.is_empty:
                    await self.updvoicechannelghostystatus(player.channel.id, "?play <query> | GhoSty")
                elif player.current:
                    await self.updvoicechannelghostystatus(player.channel.id, f"{player.current.title} | GhoSty")
        except Exception as e:
            print(f"Voice status update failed after skip: {e}")

    @commands.command(aliases=["Ap"])
    async def Autoplay(self, ctx: commands.Context) -> None:
        """Toggle autoplay on/off."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return
        
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

        if player.autoplay == wavelink.AutoPlayMode.enabled:
            player.autoplay = wavelink.AutoPlayMode.disabled
            ghostyautodisableembed = discord.Embed(
                title="",
                description=f"-# {Ghostyemojis.get('autoplay')} Autoplay is now disabled.",
                color=Ghostycolor
            )
            await ctx.send(embed=ghostyautodisableembed)
        else:
            player.autoplay = wavelink.AutoPlayMode.enabled
            ghostyautoenableembed = discord.Embed(
                title="",
                description=f"-# {Ghostyemojis.get('autoplay')} Autoplay is now enabled.",
                color=Ghostycolor
            )
            await ctx.send(embed=ghostyautoenableembed)


    @commands.command()
    async def Pause(self, ctx: commands.Context) -> None:
        """Pause the currently playing track."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player.current:
            nonewghostyemb = discord.Embed(
                title="",
                description=f"-# {Ghostyemojis.get('error')} Nothing is playing right now.",
                color=Ghostycolor
            )
            await ctx.send(embed=nonewghostyemb)
            return

        await player.pause(True)
        pausedghostyemb = discord.Embed(
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Paused player.",
            color=Ghostycolor
        )
        await ctx.send(embed=pausedghostyemb)
        await self.updvoicechannelghostystatus(player.channel.id, "Paused | GhoSty")

    @commands.command()
    async def Resume(self, ctx: commands.Context) -> None:
        """Resume the currently paused track."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player.paused:
            alrghostyrunn = discord.Embed(
                title="",
                description=f"-# {Ghostyemojis.get('error')} The player is not paused.",
                color=Ghostycolor
            )
            await ctx.send(embed=alrghostyrunn)
            return

        await player.pause(False)
        resumeghostyemb = discord.Embed(
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Resumed player.",
            color=Ghostycolor
        )
        await ctx.send(embed=resumeghostyemb)
        await self.updvoicechannelghostystatus(player.channel.id, f"{player.current.title} | GhoSty")

    @commands.command(aliases=["Bass", "Bb"])
    async def Bassboost(self, ctx: commands.Context) -> None:
        """Apply Bassboost filter."""
        
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return
        
        player: wavelink.Player = ctx.voice_client

        filters = wavelink.Filters()
    
        filters.equalizer.set(bands=[
            {"band": 0, "gain": 0.8},     
            {"band": 1, "gain": 0.7},     
            {"band": 2, "gain": 0.6},     
            {"band": 3, "gain": 0.3},     
            {"band": 4, "gain": 0.0},     
            {"band": 5, "gain": 0.0},     
            {"band": 6, "gain": 0.0},     
            {"band": 7, "gain": 0.0},     
            {"band": 8, "gain": 0.0},     
            {"band": 9, "gain": 0.0}      
        ])

    
        filters.timescale.set(
            speed=1.0,
            pitch=0.98,
            rate=1.0
        )

        await player.set_filters(filters)
        bassboostghostyemb = discord.Embed( 
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Bassboost filter applied.",
            color=Ghostycolor
        )
        await ctx.send(embed=bassboostghostyemb)

    @commands.command()
    async def Nightcore(self, ctx: commands.Context) -> None:
        """Apply Nightcore filter."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return
     
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        filters: wavelink.Filters = player.filters
        filters.timescale.set(pitch=1.2, speed=1.2, rate=1)
        await player.set_filters(filters)
        nightcoreghostyemb = discord.Embed( 
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Nightcore filter applied.",
            color=Ghostycolor
        )

        await ctx.send(embed=nightcoreghostyemb)

    @commands.command()
    async def Lofi(self, ctx: commands.Context) -> None:
        """Apply Lofi filter."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return
        
        player: wavelink.Player = ctx.voice_client

        filters = wavelink.Filters()
        
        filters.timescale.set(
            speed=0.8,     
            pitch=0.8,     
            rate=1.0        
        )
        
        filters.equalizer.set(bands=[
            {"band": 0, "gain": 0.25},   
            {"band": 1, "gain": 0.15},   
            {"band": 2, "gain": 0.05},   
            {"band": 3, "gain": -0.05},  
            {"band": 4, "gain": -0.1},   
            {"band": 5, "gain": -0.1},   
            {"band": 6, "gain": -0.05},  
            {"band": 7, "gain": 0.0},    
            {"band": 8, "gain": 0.0},    
            {"band": 9, "gain": 0.0},    
            {"band": 10, "gain": -0.05}, 
            {"band": 11, "gain": -0.1},  
            {"band": 12, "gain": -0.1},  
            {"band": 13, "gain": -0.15}, 
            {"band": 14, "gain": -0.2},  
        ])
        
        filters.low_pass.set(
            smoothing=1.5    
        )
        
        await player.set_filters(filters)
        lofighostyemb = discord.Embed( 
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Lofi filter applied.",
            color=Ghostycolor
        )

        await ctx.send(embed=lofighostyemb)




    @commands.command()
    async def Concert(self, ctx: commands.Context) -> None:
        """Apply Concert filter."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

        filters = wavelink.Filters()

        
        filters.equalizer.set(bands=[
            {"band": 0, "gain": 0.4},
            {"band": 1, "gain": 0.3},
            {"band": 2, "gain": 0.2},
            {"band": 3, "gain": 0.2},
            {"band": 4, "gain": 0.15},
            {"band": 5, "gain": 0.1},
            {"band": 6, "gain": 0.2},
            {"band": 7, "gain": 0.3},
            {"band": 8, "gain": 0.3},
            {"band": 9, "gain": 0.2}
        ])

        
        filters.timescale.set(
            speed=1.0,
            pitch=1.0,
            rate=1.02
        )

        
        filters.channel_mix.set(
            left_to_left=1.0,
            left_to_right=0.0,
            right_to_left=0.0,
            right_to_right=1.0
        )

        try:
            await player.set_filters(filters)
            concertghostyemb = discord.Embed( 
                title="",
                description=f"-# {Ghostyemojis.get('check')} | Concert filter applied.",
                color=Ghostycolor
            )
            await ctx.send(embed=concertghostyemb)
        except wavelink.exceptions.LavalinkException as e:
            print(f"{e}")


    @commands.command(aliases=["Cf", "Clearfilters"])
    async def Clearfilter(self, ctx: commands.Context) -> None:
        """Clear all active audio filters."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        filters = wavelink.Filters()  
        await player.set_filters(filters)
        clearfghostyemb = discord.Embed( 
            title="",
            description=f"-# {Ghostyemojis.get('check')} | All audio filters cleared.",
            color=Ghostycolor
        )

        await ctx.send(embed=clearfghostyemb)

    @commands.command(name="SlowedReverb", aliases=["Slowed", "Reverb", "Slow", "Slowreverb"])
    async def SlowedReverb(self, ctx: commands.Context) -> None:
        """Apply Slowed + Reverb effect."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        
        filters = wavelink.Filters()

        
        filters.timescale.set(
            speed=0.8,    
            pitch=0.9,    
            rate=1.0
        )

        
        filters.karaoke.set(
            level=0.4,        
            mono_level=0.2,   
            filter_band=500.0,  
            filter_width=100.0  
        )

        
        filters.low_pass.set(
            smoothing=1.5  
        )

        
        filters.equalizer.set(bands=[
            {"band": 0, "gain": 0.5},  
            {"band": 1, "gain": 0.3}   
        ])

        await player.set_filters(filters)
        slowrevghostyemb = discord.Embed( 
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Slowed + Reverb filter applied.",
            color=Ghostycolor
        )
        await ctx.send(embed=slowrevghostyemb)

    @commands.command(name="Tremolo", aliases=["Trem"])
    async def Tremolo(self, ctx: commands.Context) -> None:
        """Apply Tremolo filter."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        
        filters = wavelink.Filters()

        
        filters.tremolo.set(
            frequency=5.0,  
            depth=0.8       
        )

        
        filters.low_pass.set(
            smoothing=1.2
        )

        
        filters.equalizer.set(bands=[
            {"band": 0, "gain": 0.6},  
            {"band": 1, "gain": 0.4}   
        ])

        
        await player.set_volume(min(player.volume, 90))

        await player.set_filters(filters)
        tremghostyemb = discord.Embed( 
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Tremolo filter applied.",
            color=Ghostycolor
        )
        await ctx.send(embed=tremghostyemb)

    @commands.command(name="Vibrato")
    async def Vibrato(self, ctx: commands.Context) -> None:
        """Apply Vibrato filter."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        
        filters = wavelink.Filters()

        
        filters.vibrato.set(
            frequency=7.0,  
            depth=0.9        
        )

        
        filters.karaoke.set(
            level=0.25,      
            mono_level=0.18,
            filter_band=1000.0,
            filter_width=200.0
        )

        
        filters.equalizer.set(bands=[
            {"band": 0, "gain": 0.7},  
            {"band": 1, "gain": 0.5}   
        ])

        
        filters.low_pass.set(smoothing=1.4)

        
        await player.set_volume(min(player.volume, 85))

        await player.set_filters(filters)
        vibratoghostyemb = discord.Embed( 
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Vibrato filter applied.",
            color=Ghostycolor
        )
        await ctx.send(embed=vibratoghostyemb)

    @commands.command(name="8d")
    async def Eightd(self, ctx):
        """Apply 8D filter."""

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        filters = wavelink.Filters()
    
        filters.rotation.set(rotation_hz=0.28)  
    
        filters.equalizer.set(bands=[
            {"band": 0, "gain": 0.1},  
            {"band": 6, "gain": 0.15}   
        ])
        await player.set_filters(filters)
        eightdghostyemb = discord.Embed( 
            title="",
            description=f"-# {Ghostyemojis.get('check')} | 8D filter applied.",
            color=Ghostycolor
        )
        await ctx.send(embed=eightdghostyemb)

    @commands.command(name="Dolby", aliases=["Cinema", "Atmos", "Cinematic", "SurroundSound"])
    async def Dolby(self, ctx: commands.Context) -> None:
        """Apply Dolby filter."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        
        filters = wavelink.Filters()

        
        filters.rotation.set(rotation_hz=0.22)  

        filters.channel_mix.set(
            left_to_left=0.8,    
            left_to_right=0.2,   
            right_to_right=0.8,  
            right_to_left=0.2     
        )

        
        filters.equalizer.set(bands=[
            {"band": 0, "gain": 0.15},  
            {"band": 1, "gain": 0.1},   
            {"band": 9, "gain": 0.2}    
        ])

        filters.low_pass.set(smoothing=1.4)

        
        filters.karaoke.set(
            level=0.12,       
            mono_level=0.08,
            filter_band=800.0,
            filter_width=150.0
        )

        
        await player.set_volume(min(player.volume, 90))

        await player.set_filters(filters)
        atmosghostyemb = discord.Embed( 
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Dolby Surround Sound Atmos filter applied.",
            color=Ghostycolor
        )
        await ctx.send(embed=atmosghostyemb)  

    @commands.command(name="Heaven")
    async def Heaven(self, ctx: commands.Context) -> None:
        """Apply Heaven filter."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        
        filters = wavelink.Filters()

        
        filters.timescale.set(
            speed=0.85,   
            pitch=0.9,    
            rate=1.0
        )

        
        filters.rotation.set(rotation_hz=0.1)  
        filters.channel_mix.set(
            left_to_left=0.85,
            left_to_right=0.15,
            right_to_right=0.85,
            right_to_left=0.15
        )

        
        filters.equalizer.set(bands=[
            {"band": 0, "gain": 0.15},  
            {"band": 1, "gain": 0.15},  
            {"band": 9, "gain": 0.20}   
        ])

        
        filters.karaoke.set(
            level=0.25,
            mono_level=0.15,
            filter_band=650.0,
            filter_width=125.0
        )
        filters.low_pass.set(smoothing=1.6)

        
        await player.set_volume(min(player.volume, 85))

        await player.set_filters(filters)
        heavenghostyemb = discord.Embed( 
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Heaven filter applied.",
            color=Ghostycolor
        )
        await ctx.send(embed=heavenghostyemb)

    @commands.command(name="instrumental", aliases=["vocalscut", "karaoke"])
    async def instrumental(self, ctx: commands.Context) -> None:
        """Remove vocals to simulate an instrumental version."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

        filters = wavelink.Filters()

    
        filters.karaoke.set(
            level=1.0,          
            mono_level=1.0,     
            filter_band=220.0,  
            filter_width=200.0  
        )

        await player.set_filters(filters)
        await player.set_volume(min(player.volume, 90))
        instrumentalghostyemb = discord.Embed( 
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Instrumental filter applied.",
            color=Ghostycolor
        )
        await ctx.send(embed=instrumentalghostyemb)

    @commands.command(name="muffled", aliases=["underwater", "muffle"])
    async def muffled(self, ctx: commands.Context) -> None:
        """Apply a smooth Muffled effect."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

        filters = wavelink.Filters()

    
        filters.low_pass.set(smoothing=5.5)  

    
        filters.equalizer.set(bands=[
            {"band": 0, "gain": 0.1},    
            {"band": 1, "gain": 0.05},   
            {"band": 4, "gain": -0.15},  
            {"band": 5, "gain": -0.25}, 
            {"band": 9, "gain": -0.35}  
        ])


        filters.karaoke.set(
            level=0.15,
            mono_level=0.1,
            filter_band=1200.0,
            filter_width=200.0
        )

        await player.set_volume(min(player.volume, 85))

        await player.set_filters(filters)
        muffledghostyemb = discord.Embed( 
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Muffled filter applied.",
            color=Ghostycolor
        )
        await ctx.send(embed=muffledghostyemb)

    @commands.command(name="rotation", aliases=["hall", "reverbx", "cave"])
    async def echohall(self, ctx: commands.Context) -> None:
        """Apply a wide echo chamber / reverb hall effect."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

        filters = wavelink.Filters()

    
        filters.tremolo.set(frequency=2.0, depth=0.25)

    
        filters.rotation.set(rotation_hz=0.5)

    
        filters.low_pass.set(smoothing=2.8)

    
        filters.equalizer.set(bands=[
            {"band": 1, "gain": 0.1},
            {"band": 2, "gain": 0.15},
            {"band": 3, "gain": 0.2},
            {"band": 6, "gain": -0.1},
            {"band": 8, "gain": -0.2}
        ])

        await player.set_filters(filters)
        await player.set_volume(min(player.volume, 85))  
        echohallghostyemb = discord.Embed( 
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Rotation filter applied.",
            color=Ghostycolor
        )
        await ctx.send(embed=echohallghostyemb)

    @commands.command(name="reverseroom", aliases=["reversefx", "fliproom"])
    async def reverse_room(self, ctx: commands.Context) -> None:
        """Simulate reversed room reverb effect (sucked-in space feel)."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

        filters = wavelink.Filters()

    
        filters.tremolo.set(frequency=1.2, depth=0.35)

    
        filters.timescale.set(speed=0.95, pitch=0.93, rate=1.0)

    
        filters.equalizer.set(bands=[
            {"band": 0, "gain": -0.1},
            {"band": 2, "gain": 0.2},
            {"band": 3, "gain": 0.25},
            {"band": 4, "gain": -0.2},
            {"band": 7, "gain": -0.25}
        ])

    
        filters.rotation.set(rotation_hz=0.4)

        await player.set_filters(filters)
        await player.set_volume(min(player.volume, 85))
        reversegghostyemb = discord.Embed( 
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Reversed room filter applied.",
            color=Ghostycolor
        )
        await ctx.send(embed=reversegghostyemb)

    @commands.command(name="dreamcore", aliases=["dreamy", "dream", "trance", "float"])
    async def dreamcore(self, ctx: commands.Context) -> None:
        """Apply a dreamy, floating, nightcore-inspired echo filter."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

        filters = wavelink.Filters()

    
        filters.timescale.set(speed=1.12, pitch=1.2, rate=1.0)

    
        filters.tremolo.set(frequency=3.5, depth=0.2)

    
        filters.rotation.set(rotation_hz=0.3)

    
        filters.equalizer.set(bands=[
            {"band": 1, "gain": 0.1},
            {"band": 4, "gain": 0.2},
            {"band": 5, "gain": 0.15},
            {"band": 8, "gain": 0.3}
        ])

        await player.set_filters(filters)
        await player.set_volume(min(player.volume, 90))
        dreamcoreghostyemb = discord.Embed( 
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Dreamcore filter applied.",
            color=Ghostycolor
        )
        await ctx.send(embed=dreamcoreghostyemb)

    @commands.command(aliases=["Vol"])
    async def Volume(self, ctx: commands.Context, value: int) -> None:
        """Change the volume of the player."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):           
            return
        
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        await player.set_volume(value)
        volumeghostyemb = discord.Embed(
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Volume set to {value}.",
            color=Ghostycolor
        )
        await ctx.send(embed=volumeghostyemb)

    @commands.command(aliases=["Stop", "Dc"])
    async def Disconnect(self, ctx: commands.Context) -> None:
        """Stop and Disconnect the Player."""
        if not await self.checkchannelghostyok(ctx):
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

        if not player:
            ghostyw0embed = discord.Embed(
                title="",
                description=f"-# {Ghostyemojis.get('error')} | I'm not even connected to a voice channel.",
                color=Ghostycolor
            )
            await ctx.send(embed=ghostyw0embed)
            return


        await player.disconnect()

        ghostydcemb = discord.Embed(
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Yeehaw, I’m out! Disconnecting.",
            color=Ghostycolor
        )
        await ctx.send(embed=ghostydcemb)


    @commands.command(name="Queue", aliases=["Q"])
    async def Queue(self, ctx: commands.Context):
        """Displays the current music queue."""
        player: wavelink.Player = ctx.voice_client
        if not player or not player.current:
            ghostyw01embed = discord.Embed(
                title="",
                description=f"-# {Ghostyemojis.get('error')} | I'm not even connected to a voice channel.",
                color=Ghostycolor
            )
            await ctx.send(embed=ghostyw01embed)
            return

        view = ghostyqview(ctx, player)
        embed = view.ghostyformatph()
        view.message = await ctx.send(embed=embed, view=view)




    async def okGhostyfetchsim(self, okGHOSTYvidid: str, cap: int = 7):
        if not okGHOSTYvidid:
            return []

        url = f"https://www.youtube.com/watch?v={okGHOSTYvidid}&list=RD{okGHOSTYvidid}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    return []
                text = await resp.text()

        import re
        match = re.search(r"ytInitialData\s*=\s*(\{.*?\});", text, re.DOTALL)
        if not match:
            return []

        import json
        try:
            ytghostyd = json.loads(match.group(1))
            playghostyl = ytghostyd.get("contents", {}) \
                .get("twoColumnWatchNextResults", {}) \
                .get("playlist", {}) \
                .get("playlist", {}) \
                .get("contents", [])
        except Exception:
            return []

        tracks = []
        for item in playghostyl:
            if len(tracks) >= cap:
                break
            v = item.get("playlistPanelVideoRenderer")
            if not v:
                continue
            vid = v.get("videoId")
            if not vid or vid == okGHOSTYvidid:
                continue
            title = None
            try:
                title = v.get("title", {}).get("runs", [{}])[0].get("text")
            except Exception:
                title = None
            if not title:
                title = v.get("title", {}).get("simpleText", "Unknown")
            tracks.append({
                "title": title,
                "identifier": vid,
                "url": f"https://www.youtube.com/watch?v={vid}"
            })
        return tracks






    @commands.command(name="Similar", aliases=["Sim"])
    async def Similar(self, ctx: commands.Context):
        """Fetch Similar tracks to the currently playing track."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return

        player: wavelink.Player = ctx.voice_client

        okGHOSTYvidid = None
        
        if hasattr(player.current, "identifier"):
            okGHOSTYvidid = player.current.identifier
        elif hasattr(player.current, "uri"):
            import urllib.parse
            query = urllib.parse.urlparse(player.current.uri).query
            params = urllib.parse.parse_qs(query)
            okGHOSTYvidid = params.get("v", [None])[0]

        if not okGHOSTYvidid:
            await ctx.send("Couldn't find a valid YouTube video ID from the current track.")
            return

        tracks = await self.okGhostyfetchsim(okGHOSTYvidid, cap=10)
        if not tracks:
            await ctx.send("No similar tracks found.")
            return

        description = f"{Ghostyemojis.get('cd')} | Select tracks from the dropdown below to add them to the queue.\n\n"
        for idx, track in enumerate(tracks, start=1):
            description += f"-# {idx}. [{track['title']}]({track['url']})\n"

        embed = discord.Embed(
            title="",
            description=description,
            color=Ghostycolor
        )

        view = View(timeout=60)
        view.add_item(SimGhostyMenu(tracks, player, ctx.author.id))

        await ctx.send(embed=embed, view=view)

    @commands.command(name="Remove")
    async def remove_track(self, ctx: commands.Context, index: int):
        """Remove a track from the queue."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return
        
        player: wavelink.Player = ctx.voice_client

        if not player or not player.queue:
            ghostynoq = discord.Embed( 
                title="",
                description=f"-# {Ghostyemojis.get('error')} | No songs in the queue to remove.",
                color=Ghostycolor
            )
            return await ctx.send(embed=ghostynoq)

        queue = list(player.queue)

        if index < 1 or index > len(queue):
            ghostynonum = discord.Embed(
                title="",
                description=f"-# {Ghostyemojis.get('error')} | Invalid number. Enter a number between 1 and {len(queue)}.",
                color=Ghostycolor
            )
            return await ctx.send(embed=ghostynonum)

        removed_track = queue[index - 1]


        player.queue.remove(removed_track)
        
        sghostyok = discord.Embed(
            title="",
            description=f"-# {Ghostyemojis.get('check')} | Removed **{removed_track.title}** from the queue.",
            color=Ghostycolor
        )
        await ctx.send(embed=sghostyok)

    @commands.command(name="Nowplaying", aliases=["Np", "Now"])
    async def Nowplaying(self, ctx):
        """Display the currently playing track."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return

        player: wavelink.Player = ctx.voice_client
        track = player.current

        embed = discord.Embed(
            title=f"{Ghostyemojis.get('cd')} | Now Playing",
            description=f"[{track.title}]({track.uri})",
            color=Ghostycolor
        )
        embed.set_thumbnail(url=track.artwork)
        embed.add_field(name=f"{Ghostyemojis.get('clock')} | Duration", value=f"`{self.formatghostytm(track.length)}`", inline=True)
        embed.add_field(name=f"{Ghostyemojis.get('user')} | Author", value=f"`{track.author}`", inline=True)
        embed.set_footer(text="Made By @ghostyjija", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)

        msg = await ctx.send(embed=embed)
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=60))
        try:
            await msg.delete()
        except discord.NotFound:
            pass  

    def formatghostytm(self, ms: int) -> str:
        seconds = ms // 1000
        minutes = seconds // 60
        remainghostyolaf1 = seconds % 60
        return f"{minutes}:{remainghostyolaf1:02d}"

    @commands.command(name="Loop")
    async def loop(self, ctx):
        """Toggle Loop mode."""
        if not await self.checkchannelghostyok(ctx):
            return
        if not await self.ghostyplaycheck(ctx):
            return
        
        player: wavelink.Player = ctx.voice_client

        loop_mode = player.queue.mode
        status_map = {
            wavelink.QueueMode.loop: "Looping **track**",
            wavelink.QueueMode.loop_all: "Looping **queue**",
            wavelink.QueueMode.normal: "Looping **disabled**"
        }

        embed = discord.Embed(
            title="",
            description=status_map.get(loop_mode, "Unknown"),
            color=Ghostycolor
        )

        view = Loopghostyview(player, ctx.author.id)
        msg = await ctx.send(embed=embed, view=view)
        view.message = msg
        await view.wait()

    @commands.command(name="Dailyhits", aliases=["Dh", "Genre", "Hits"])
    async def Dailyhits(self, ctx):
        """Choose a genre and add daily hit songs to the queue."""
        if not await self.checkchannelghostyok(ctx):
            return

   
        if not ctx.voice_client:
            if ctx.author.voice and ctx.author.voice.channel:
 
                channel = ctx.author.voice.channel
                await channel.connect(cls=wavelink.Player)  

        view = Dhitsghostyview(self.bot, ctx, self.okGhostyfetchsim)
        olghostyem = discord.Embed(
            title="",
            description=f"-# {Ghostyemojis.get('rightarrow')} | Choose a genre of your choice to fetch Tracks.",
            color=Ghostycolor
        )
        await ctx.send(embed=olghostyem, view=view)





async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Music(bot))
