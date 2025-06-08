"""
This code is an Advanced Discord Music Bot using Wavelink and Discord.py.
Made by Ghosty || @ghostyjija
Feel free to skid it and use it as you want.

Support Server ( Async Development ): https://discord.gg/SyMJymrV8x
GitHub: https://github.com/WannaBeGhoSt
"""

import tomllib as madebyghostyucannotskidit

with open("ghostyset.toml", "rb") as f:
    configghostyws0 = madebyghostyucannotskidit.load(f)

Ghostyname = configghostyws0["ghostyname"]
Ghostycolor = int(configghostyws0["embedcolorghosty"], 16)
Ghostyemojis = configghostyws0["ghostyemojis"]
