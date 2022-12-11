#!/bin/python3
#--------------------------------------------------------------------
# Module: Turtle
# Purpose: Module for the bot to interface with the Turtle.
# Author: Dylan Sperrer (p0t4t0sandwich|ThePotatoKing)
# Date: 25NOVEMBER2022
# Updated: <date> <author>
#--------------------------------------------------------------------
import ast
from discord.ext import commands
import discord
from aiohttp import ClientSession
from PIL import Image
from PIL.Image import Resampling
import json
import os
from io import BytesIO
import base64

import bot_library as b
import cct_turtle_api as cct

def decode_img(base64_img: bytes) -> Image:
    return Image.open(
        BytesIO(
            base64.b64decode(ast.literal_eval(base64_img)
            )
        )
    ).convert('RGBA')

async def get_surrounding_blocks(status) -> dict:
    block_names = {}
    block_names["up"] = status["up"]
    block_names["down"] = status["down"]
    block_names["front"] = status["front"]
    block_names["back"] = status["back"]
    block_names["left"] = status["left"]
    block_names["right"] = status["right"]
    return block_names

cache = {}

with open("textures.json", "r") as f:
    texture_storage = json.loads(f.read())
    for block in texture_storage.keys():
        cache[block] = decode_img(texture_storage[block])

async def get_surrounding_textures(status) -> dict:
    textures = {}
    blocks = {}
    blocks["up"] = status["up"]
    blocks["down"] = status["down"]
    blocks["front"] = status["front"]
    blocks["back"] = status["back"]
    blocks["left"] = status["left"]
    blocks["right"] = status["right"]
    for key in blocks.keys():
        block = blocks[key]
        if block in cache.keys():
            textures[key] = cache[block]
        else:
            if block not in [None, "minecraft:air", "nil"]:
                stuff = block.split(":")
                textures[key] = decode_img(texture_storage[block]) # Image.open(f"../textures/{stuff[0]}/{stuff[1]}.png").convert("RGB")
            else:
                textures[key] = decode_img(texture_storage["minecraft:air"]) # Image.open("../textures/minecraft/air.png").convert("RGB")
            cache[block] = textures[key]
    return textures

async def image_resize(image: Image) -> Image:
    return image.resize((image.width*12, image.height*12), resample=Resampling.BOX)

async def turtle_image(status):
    from PIL import Image

    textures = await get_surrounding_textures(status)

    size = (16*3,16*3)

    result = Image.new('RGB', size, (47, 49, 54))
    result.paste(im=textures["front"], box=(16, 16))
    result.paste(im=textures["up"], box=(16, 0))
    result.paste(im=textures["down"], box=(16, 32))
    result.paste(im=textures["left"], box=(0, 16))
    result.paste(im=textures["right"], box=(32, 16))
    result.paste(im=textures["back"], box=(32, 0))

    image = await image_resize(result)
    return image

async def get_image(status) -> None:
    import supabase_interface
    from io import BytesIO

    image = await supabase_interface.turtle_image(status)

    with BytesIO() as image_binary:
        image.save(image_binary, 'PNG')
        image_binary.seek(0)
        return discord.File(fp=image_binary, filename='image.png')

async def get_embed(text) -> discord.Embed | discord.File:
    # Init variables
    image = f"attachment://image.png"

    title = f"Turtle Test"
    description = f"{text}"

    # Add Colour
    color = 0x65bf65

    # Output Discord Embed object
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_image(url=image)
    file = await get_image(text)

    return (embed, file)

class Turtle(commands.Cog, discord.ui.View):
    def __init__(self, bot) -> None:
        discord.ui.View.__init__(self, timeout=None)
        self.bot = bot
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 1.5, commands.BucketType.guild)
        self.turtle_dict = {}

    async def turtle_check(self, label):
        if label not in self.turtle_dict.keys():
            self.turtle_dict[label] = cct.Turtle(label, os.getenv("PUBLIC_TURTLE_API"))

    async def button_logic(self, interaction: discord.Interaction, turtle: dict):
        interaction.message.author = interaction.user
        bucket = self.cooldown.get_bucket(interaction.message)
        retry = bucket.update_rate_limit()
        if not retry:
            await interaction.response.defer()
            embed, file = await get_embed(turtle)
            await interaction.message.edit(embed=embed, attachments=[file])
        else:
            await interaction.response.defer()


    @discord.ui.button(emoji='🔄', style=discord.ButtonStyle.grey, custom_id='persistent_view:status', row=1)
    async def status(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        guild_id = str(interaction.guild_id)
        await self.turtle_check(guild_id)
        await self.button_logic(interaction, await self.turtle_dict[guild_id].status())

    @discord.ui.button(emoji="🔼", style=discord.ButtonStyle.gray, custom_id='persistent_view:forward', row=1)
    async def forward(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        guild_id = str(interaction.guild_id)
        await self.turtle_check(guild_id)
        await self.button_logic(interaction, await self.turtle_dict[guild_id].forward())

    @discord.ui.button(emoji="⏫", style=discord.ButtonStyle.gray, custom_id='persistent_view:up', row=1)
    async def up(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        guild_id = str(interaction.guild_id)
        await self.turtle_check(guild_id)
        await self.button_logic(interaction, await self.turtle_dict[guild_id].up())

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.gray, custom_id='persistent_view:turnLeft', row=2)
    async def turnLeft(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        guild_id = str(interaction.guild_id)
        await self.turtle_check(guild_id)
        await self.button_logic(interaction, await self.turtle_dict[guild_id].turnLeft())

    @discord.ui.button(emoji="⛏️", style=discord.ButtonStyle.gray, custom_id='persistent_view:dig', row=2)
    async def dig(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        guild_id = str(interaction.guild_id)
        await self.turtle_check(guild_id)
        await self.button_logic(interaction, await self.turtle_dict[guild_id].dig())

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.gray, custom_id='persistent_view:turnRight', row=2)
    async def turnRight(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        guild_id = str(interaction.guild_id)
        await self.turtle_check(guild_id)
        await self.button_logic(interaction, await self.turtle_dict[guild_id].turnRight())

    @discord.ui.button(emoji="❔", style=discord.ButtonStyle.gray, custom_id='persistent_view:help', row=3)
    async def help(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        guild_id = str(interaction.guild_id)
        await self.turtle_check(guild_id)

    @discord.ui.button(emoji="🔽", style=discord.ButtonStyle.gray, custom_id='persistent_view:back', row=3)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        guild_id = str(interaction.guild_id)
        await self.turtle_check(guild_id)
        await self.button_logic(interaction, await self.turtle_dict[guild_id].back())

    @discord.ui.button(emoji="⏬", style=discord.ButtonStyle.gray, custom_id='persistent_view:down', row=3)
    async def down(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        guild_id = str(interaction.guild_id)
        await self.turtle_check(guild_id)
        await self.button_logic(interaction, await self.turtle_dict[guild_id].down())

    @discord.ui.button(label="⛏️ ⏫", style=discord.ButtonStyle.gray, custom_id='persistent_view:digMoveUp', row=1)
    async def digMoveUp(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        guild_id = str(interaction.guild_id)
        await self.turtle_check(guild_id)
        await self.button_logic(interaction, await self.turtle_dict[guild_id].digMoveUp())

    @discord.ui.button(label="⛏️ 🔼", style=discord.ButtonStyle.gray, custom_id='persistent_view:digMoveForward', row=2)
    async def digMoveForward(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        guild_id = str(interaction.guild_id)
        await self.turtle_check(guild_id)
        await self.button_logic(interaction, await self.turtle_dict[guild_id].digMoveForward())

    @discord.ui.button(label="⛏️ ⏬", style=discord.ButtonStyle.gray, custom_id='persistent_view:digMoveDown', row=3)
    async def digMoveDown(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        guild_id = str(interaction.guild_id)
        await self.turtle_check(guild_id)
        await self.button_logic(interaction, await self.turtle_dict[guild_id].digMoveDown())

    @commands.command()
    async def turtle_init(self, ctx: commands.Context) -> None:
        """Initializes the Turtle"""
        # Init Variables
        channel = ctx.guild.name
        author = ctx.author.name
        author_id = ctx.author.id
        content = ctx.message.content
        guild_id = str(ctx.guild.id)

        if ctx.author.guild_permissions.administrator or self.bot.owner_id == author_id:
            headers = {"Content-Type": "application/json"}
            data = json.dumps({"label": guild_id})

            async with ClientSession(headers=headers) as session:
                async with session.post(url=os.getenv("PRIVATE_TURTLE_API") + "initNewTurtle", data=data) as post:
                    response = await post.json()
                    post.close()

            # Log the output
            self.bot.log(channel, author, content)
            self.bot.log(channel, self.bot.user, response)
            await ctx.send(response["message"])

    @commands.command()
    async def view(self, ctx: commands.Context) -> None:
        """Creates an embed to check server status"""
        channel = ctx.guild.name
        author = ctx.author
        content = ctx.message.content

        guild_id = str(ctx.guild.id)
        await self.turtle_check(guild_id)

        embed, file = await get_embed(await self.turtle_dict[guild_id].status())

        # Log the output
        self.bot.log(channel, author, content)
        self.bot.log(channel, self.bot.user, embed.description)

        await ctx.send(embed=embed, file=file, view=self)

async def setup(bot: commands.bot) -> None:
    await bot.add_cog(Turtle(bot))
    bot.add_view(Turtle(bot))