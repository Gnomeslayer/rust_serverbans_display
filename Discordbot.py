import asyncio, os, discord.utils
from discord.ext import commands
import json

""" 
You will need a new bot token, so follow this quick guide on how to create a bot:
https://discordpy.readthedocs.io/en/latest/discord.html
"""

# Your Bot token goes here.
with open("config.json", "r") as f:
    config = json.load(f)
BOT_TOKEN: str = config["discord_token"]

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=config["prefix"], intents=intents)


@bot.event
async def on_ready():
    print("Bot is ready")


# Loads the cogs
@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    await bot.load_extension(f"cogs.{extension}")
    await ctx.channel.send(f"Loaded {extension}")


@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await ctx.channel.send(f"Unloaded {extension}")


@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    extension = extension.lower()
    await bot.unload_extension(f"cogs.{extension}")
    await asyncio.sleep(1)
    await bot.load_extension(f"cogs.{extension}")
    await ctx.channel.send(f"Reloaded {extension}")


async def setup():
    # Location of the COG files.
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            if "bm" not in filename:
                await bot.load_extension(f"cogs.{filename[:-3]}")

    await bot.start(BOT_TOKEN)


asyncio.run(setup())