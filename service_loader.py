
import platform
import os
import nacl

import discord
from discord.ext import tasks
from discord.ext.commands import Bot, Context

from constants import *


def loadListeners(bot: Bot) -> None:

    @bot.event
    async def on_ready() -> None:
        bot.logger.info(f"Logged in as {bot.user.name}")
        bot.logger.info(f"discord.py API version: {discord.__version__}")
        bot.logger.info(f"Python version: {platform.python_version()}")
        bot.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        bot.logger.info("-------------------")

        channel = bot.get_channel(
            int(bot.configuration[CONF_CHANNEL_VOICE]))

        try:
            bot.channel = await channel.connect()
        except Exception as e:
            print(e)

        status_task.start()
        if bot.configuration[CONF_SYNC_COMMANDS_GLOBALLY]:
            bot.logger.info("Syncing commands globally...")
            await bot.tree.sync()

    @tasks.loop(minutes=1.0)
    async def status_task() -> None:
        pass
        # bot.logger.debug(f"Updating presence status")
        # await bot.change_presence(activity=discord.Game(DISCORD_STATUS_PLAYING))

    @bot.event
    async def on_message(message: discord.Message) -> None:
        if message.author == bot.user or message.author.bot:
            return

        await bot.process_commands(message)

    @bot.event
    async def on_command_completion(context: Context) -> None:
        full_command_name = context.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])

        if context.guild is not None:
            bot.logger.info(
                f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})"
            )
        else:
            bot.logger.info(
                f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs"
            )


async def loadCogs(bot: Bot) -> None:
    for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/{FOLDER_COGS}"):
        if file.endswith(".py"):
            extension = file[:-3]

            try:
                await bot.load_extension(f"{FOLDER_COGS}.{extension}")
                bot.logger.info(f"Loaded extension: '{extension}'")

            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                bot.logger.error(
                    f"Failed to load extension: {extension}\n{exception}"
                )
