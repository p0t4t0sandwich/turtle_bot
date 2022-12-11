#!/bin/python3
#--------------------------------------------------------------------
# Module: Hot Reload
# Purpose: Program built hot reload changes to Cogs.
# Author: Dylan Sperrer (p0t4t0sandwich|ThePotatoKing)
# Date: 18NOVEMBER2022
# Updated: <date> <author>
#--------------------------------------------------------------------

from discord.ext import commands

import os

import bot_library as b

class HotReload(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def hotreload(self, ctx: commands.Context, *args) -> None:
        if args[0] == "all":
            for folder in os.listdir("modules"):
                if os.path.exists(os.path.join("modules", folder, "cog.py")):
                    b.bot_logger(self.bot.path, self.bot.name, f"Cog {folder} has been reloaded")
                    await self.bot.reload_extension(f"modules.{folder}.cog")
        else:
            for i in args:
                b.bot_logger(self.bot.path, self.bot.name, f"Cog {i} has been reloaded")
                await self.bot.reload_extension(f"modules.{i}.cog")

async def setup(bot: commands.bot) -> None:
    await bot.add_cog(HotReload(bot))