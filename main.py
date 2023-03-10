from constants import *
import service_loader

import asyncio
import json
import logging
import os
import sys

import discord
from discord.ext import commands
from discord.ext.commands import Bot, Context

import database_manager

configuration: dict = None
robot: Bot = None


def loadConfigurationSettings() -> None:
    global configuration

    if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/{FILE_CONFIGURATION_NAME}"):
        sys.exit(
            f"'{FILE_CONFIGURATION_NAME}' not found! Please add it and try again."
        )

    with open(f"{os.path.realpath(os.path.dirname(__file__))}/{FILE_CONFIGURATION_NAME}") as configurationFile:
        configuration = json.load(configurationFile)


def initializeLogging() -> None:
    class LoggingFormatter(logging.Formatter):
        # Colors
        black = "\x1b[30m"
        red = "\x1b[31m"
        green = "\x1b[32m"
        yellow = "\x1b[33m"
        blue = "\x1b[34m"
        gray = "\x1b[38m"
        # Styles
        reset = "\x1b[0m"
        bold = "\x1b[1m"

        COLORS = {
            logging.DEBUG: gray + bold,
            logging.INFO: blue + bold,
            logging.WARNING: yellow + bold,
            logging.ERROR: red,
            logging.CRITICAL: red + bold
        }

        def format(self, record: logging.LogRecord) -> str:
            log_color = self.COLORS[record.levelno]
            format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
            format = format.replace("(black)", self.black + self.bold)
            format = format.replace("(reset)", self.reset)
            format = format.replace("(levelcolor)", log_color)
            format = format.replace("(green)", self.green + self.bold)
            formatter = logging.Formatter(
                format, "%Y-%m-%d %H:%M:%S", style="{")

            return formatter.format(record)

    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(LoggingFormatter())

    file_handler: logging.FileHandler = logging.FileHandler(
        filename=FILE_LOG, encoding="utf-8", mode="w"
    )
    file_handler.setFormatter(logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
    ))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    robot.logger = logger


def initializeBot() -> None:
    global robot

    intents = discord.Intents.default()
    # intents.voice_states = True

    robot = Bot(
        command_prefix=commands.when_mentioned_or(configuration[CONF_PREFIX]),
        intents=intents, help_command=None
    )
    robot.configuration = configuration


if __name__ == '__main__':
    loadConfigurationSettings()
    initializeBot()
    initializeLogging()

    dbFile = os.path.join(configuration[CONF_REPOSITORY_PATH], STR_SQLITE_FILE)
    robot.dbManager = database_manager.DataManager(dbFile, robot.logger)
    robot.dbManager.Initialize()

    service_loader.loadListeners(robot)
    asyncio.run(service_loader.loadCogs(robot))
    robot.run(configuration[CONF_TOKEN])
