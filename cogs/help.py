"""
This code is an Advanced Discord Music Bot using Wavelink and Discord.py.
Made by Ghosty || @ghostyjija
Feel free to skid it and use it as you want.

Support Server ( Async Development ): https://discord.gg/SyMJymrV8x
GitHub: https://github.com/WannaBeGhoSt
"""

import difflib
import discord
import os

from discord.ext import commands
from discord.ui import View, Select, Button

from ghostyconfig import Ghostyname, Ghostycolor, Ghostyemojis



class AsyncDevelopmentGhostyHelpMenuMadeByGhostyHahahaha(Select):
    def __init__(self, bot: commands.Bot, author_id: int):
        self.bot = bot
        self.author_id = author_id
        self.original_user_id = author_id

        options = []
        for cog in bot.cogs.values():
            if cog.qualified_name.lower() in ["help", "blacklist"]:
                continue  
            if not cog.get_commands():
                continue
            options.append(discord.SelectOption(
                label=cog.qualified_name,
                description=f"View commands from {cog.qualified_name}"
            ))

        super().__init__(
            placeholder="Select A Module",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.original_user_id:
            await interaction.response.send_message("You cannot interact with this element.", ephemeral=True)
            return
    
        selected_cog = self.values[0]
        cog = self.bot.get_cog(selected_cog)
        if not cog:
            await interaction.response.send_message("That category doesn't exist.", ephemeral=True)
            return
    
        embed = discord.Embed(
            title="",
            description="",
            color=Ghostycolor
        )
        embed.set_author(name=f"{selected_cog} Commands", icon_url=self.bot.user.display_avatar.url if self.bot.user else None)
    
    
        visible_commands = [cmd for cmd in cog.get_commands() if not cmd.hidden]
    
    
        if visible_commands:
            command_list = ", ".join(f"`{cmd.name}`" for cmd in visible_commands)
            embed.description = f"{command_list}"
        else:
            embed.description = f"No visible commands in **{selected_cog}**."
        
        
        await interaction.response.edit_message(embed=embed, attachments=[], view=self.view)


class AsyncDevelopmentGhostyHomebuMadeByGhostyHahahaha(Button):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__(
            style=discord.ButtonStyle.gray,
            label="",
            emoji=Ghostyemojis.get('home'),
            row=1  
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.original_user_id:
            await interaction.response.send_message("You cannot interact with this element.", ephemeral=True)
            return
        
        
        command_count = len([cmd for cmd in self.bot.commands if not cmd.hidden])
        
        
        prefix = "?"
        
        
        embed = discord.Embed(
            title="",
            description=(
                f"- Prefix For This Server ``{prefix}``\n"
                f"- Total Commands : **{command_count}**\n"
                f"- Prefix **{command_count}**\n"
                "```ansi\n"
                "[2;34m[0m[2;34mChoose A Specific Module Of Your Own Desire[0m\n"
                "```\n\n"
            ),
            color=Ghostycolor
        )
        embed.add_field(name=f"{Ghostyemojis.get('category')} **__Modules__**", value=f"‎ ‎ ‎ ‎ {Ghostyemojis.get('music')} : Music\n‎ ‎ ‎ ‎ {Ghostyemojis.get('utility')} : Utility", inline=False)
        

        await interaction.response.edit_message(embed=embed, view=self.view)


class AsyncDevelopmentGhostyHelpViewMadeByGhostyHahahaha(View):
    def __init__(self, bot: commands.Bot, author_id: int):
        super().__init__(timeout=60)
        self.original_user_id = author_id
        self.add_item(AsyncDevelopmentGhostyHelpMenuMadeByGhostyHahahaha(bot, author_id))
        self.add_item(AsyncDevelopmentGhostyHomebuMadeByGhostyHahahaha(bot))

    async def on_timeout(self):
        
        self.clear_items()

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="Help", aliases=["H"])
    async def help(self, ctx: commands.Context, *, command: str = None):
        """Show the help menu or info about a command."""
        if not command:
            
            
            prefix = "?"  
            if hasattr(self.bot, "command_prefix"):
                if callable(self.bot.command_prefix):
                    prefix_result = await self.bot.command_prefix(self.bot, ctx.message)
                    
                    if isinstance(prefix_result, list):
                        prefix = prefix_result[0]
                    else:
                        prefix = prefix_result
                else:
                    prefix = self.bot.command_prefix
            
            
            command_count = len([cmd for cmd in self.bot.commands if not cmd.hidden])
            
            embed = discord.Embed(
                title="",
                description=(
                    f"- Prefix For This Server ``{prefix}``\n"
                    f"- Total Commands : **{command_count}**\n"
                    f"- Prefix **{command_count}**\n"
                    "```ansi\n"
                    "[2;34m[0m[2;34mChoose A Specific Module Of Your Own Desire[0m\n"
                    "```\n\n"
                ),
                color=Ghostycolor
            )
            embed.add_field(name=f"{Ghostyemojis.get('category')} **__Modules__**", value=f"‎ ‎ ‎ ‎ {Ghostyemojis.get('music')} : Music\n‎ ‎ ‎ ‎ {Ghostyemojis.get('radio')} : Radio\n‎ ‎ ‎ ‎ {Ghostyemojis.get('utility')} : Utility", inline=False)

            bghostysbasedir = os.path.dirname(os.path.dirname(__file__))
            ghostyimgpath = os.path.join(bghostysbasedir, "assets", "ghostyhaqwp.jpg")
            file = discord.File(ghostyimgpath, filename="ghostyhaqwp.jpg")
            embed.set_image(url="attachment://ghostyhaqwp.jpg")
            ghostytop = discord.AllowedMentions.none()
            return await ctx.reply(embed=embed, file=file, view=AsyncDevelopmentGhostyHelpViewMadeByGhostyHahahaha(self.bot, ctx.author.id), allowed_mentions=ghostytop)


        cmd_obj = self.bot.get_command(command)
        if cmd_obj:
            embed = discord.Embed(
                title=f"",
                color=Ghostycolor
            )
            embed.set_author(name=f"{cmd_obj.name} Command Guide", icon_url=self.bot.user.display_avatar.url if self.bot.user else None)
            embed.add_field(name="Description", value=cmd_obj.help or "No description provided.", inline=False)

            if cmd_obj.aliases:
                embed.add_field(name="Aliases", value=", ".join(f"`{a}`" for a in cmd_obj.aliases), inline=False)

            embed.add_field(name="Category", value=cmd_obj.cog_name or "Uncategorized", inline=False)

            usage = f"?{cmd_obj.qualified_name} {cmd_obj.signature}" if cmd_obj.signature else f"?{cmd_obj.qualified_name}"
            embed.add_field(name="Usage", value=f"`{usage}`", inline=False)

            return await ctx.send(embed=embed)
        allcommandsnames = [cmd.name for cmd in self.bot.commands if not cmd.hidden]
        suggestions = difflib.get_close_matches(command, allcommandsnames, n=3, cutoff=0.4)


        suggest_text = "\n".join(f"`{s}`" for s in suggestions) if suggestions else "No similar commands found."
        embed = discord.Embed(
            title="",
            description=f"{Ghostyemojis.get('error')} Could not find a command named `{command}`.\n\n{Ghostyemojis.get('search')} **Did you mean:**\n{suggest_text}",
            color=Ghostycolor
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
