#!/bin/python3
#--------------------------------------------------------------------
# Project: Turtle Discord Bot
# Purpose: To allow the control of a Turtle bot from a Discord server.
# Author: Dylan Sperrer (p0t4t0sandwich|ThePotatoKing)
# Date: 25NOVEMBER2022
# Updated: <date> <author>
#--------------------------------------------------------------------

from discord.ext import commands
import discord
import os

import bot_library as b

class BASBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        self.path = "./turtle_discord_bot/"
        self.name = "turtle_discord_bot"
        self.synced = True

        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            help_command=None,
        )

    async def load_extensions(self) -> None:
        for folder in os.listdir("modules"):
            if os.path.exists(os.path.join("modules", folder, "cog.py")):
                b.bot_logger(self.path, self.name, f"Cog {folder} has been loaded")
                await self.load_extension(f"modules.{folder}.cog")

    def log(self, channel, author, content) -> None:
        b.bot_logger(self.path, self.name, f'[{channel}] [{author}] {content}')

    async def on_ready(self) -> None:
        await self.wait_until_ready()
        b.bot_logger(self.path, self.name, f"We have logged in as {self.user}")
        self.owner_id = (await self.application_info()).owner.id

        await self.load_extensions()
        if not self.synced:
            await self.tree.sync()
            self.synced = True

if __name__ == "__main__":
    bot = BASBot()
    # bot.run(token=os.getenv("BOT_ID"))
    from dotenv import load_dotenv
    load_dotenv()
    bot.run(token=os.getenv("BOT_ID"))
