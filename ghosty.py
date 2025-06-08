"""
This code is an Advanced Discord Music Bot using Wavelink and Discord.py.
Made by Ghosty || @ghostyjija
Feel free to skid it and use it as you want.

Support Server ( Async Development ): https://discord.gg/SyMJymrV8x
GitHub: https://github.com/WannaBeGhoSt
"""

import asyncio
import logging
import os

import discord
from discord.ext import commands
from ghostyconfig import Ghostyname, Ghostycolor, Ghostyemojis

import wavelink

class GhoSty(commands.Bot):
    def __init__(self) -> None:
        GhoStyIntents: discord.Intents = discord.Intents.all()

        discord.utils.setup_logging(level=logging.INFO)

        async def get_prefix(GhostyBotCl, message):
            return ["?", "? ", f"{GhostyBotCl.user.mention} "] # ghosty prefix

        super().__init__(command_prefix=get_prefix, intents=GhoStyIntents, help_command=None, case_insensitive=True)


    async def setup_hook(self) -> None:
        nodes = [
            # THIS NODE IS NOT MINE BUT YOU CAN USE IT AS IT IS PUBLIC
            wavelink.Node(uri="http://lavalink.pericsq.ro:4499", password="plamea", resume_timeout=90),
        ]
        try:
            await wavelink.Pool.connect(nodes=nodes, client=self, cache_capacity=100)
            logging.info("Wavelink connection initialized in setup_hook")
        except Exception as e:
            logging.error(f"Failed to connect to Wavelink: {e}")

    async def on_ready(self) -> None:
        logging.info("Logged in: %s | %s", self.user, self.user.id)

    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        logging.info("Wavelink Node connected: %r | Resumed: %s", payload.node, payload.resumed)

GhostyBotCl: GhoSty = GhoSty()

async def GhostyCogLoader() -> None:
    baseghostydirs = ["./cogs", "./cogs/events"]
    for bsghostydir in baseghostydirs:
        for filesghostyn in os.listdir(bsghostydir):
            if filesghostyn.endswith(".py"):
                extsghostyok = bsghostydir.replace("./", "").replace("/", ".") + f".{filesghostyn[:-3]}"
                try:
                    await GhostyBotCl.load_extension(extsghostyok)
                except Exception as e:
                    logging.error(f"Failed to load extension {extsghostyok}: {e}")

async def main() -> None:
    async with GhostyBotCl:
        await GhostyCogLoader()
        await GhostyBotCl.start("BOT TOKEN") # BOT TOKEN

asyncio.run(main())