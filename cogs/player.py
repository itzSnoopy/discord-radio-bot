from __future__ import unicode_literals

import discord
from discord.ext import commands
from discord.ext.commands import Context
import asyncio
import subprocess
import re
import os
import random
from logging import Logger

from yt_dlp import YoutubeDL
from yt_dlp import utils
import sys

import constants


class Player(commands.Cog, name="player"):
    __flagStop = False
    __flagNewSong = None

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="add", description="Add a song to the queue.")
    async def addSong(self, context: Context) -> None:
        reply = discord.Embed(description="")

        command = context.message.content.split(' ')
        if len(command) != 2 or not IsYoutubeUrl(command[1]):
            reply.description = f"To use this command, you must add a valid youtube URL as a parameter: !add {constants.STR_YOUTUBE_URL_STARTSWITH}AAABBBCCC"
            await context.send(embed=reply)
            return

        try:
            result = DownloadFromYoutube(command[1], self.bot.configuration, self.bot.logger)
            self.bot.dbManager.InsertSong(result[0], result[1])
            reply.description = "Song has been added to playlist"
        except Exception as e:
            reply.description = "This link has already been downloaded or couldnt be accessed"

        await context.send(embed=reply)

    # TO-DO: Continue here
    # Pick a random track from list
    # If argument is give, select first song containing the keyword
    @ commands.hybrid_command(name="play", description="Starts playing music.")
    async def playMusic(self, context: Context) -> None:
        reply = discord.Embed(
            description="playing..."
        )
        if not IsUser(self.bot, context):
            reply.description = "You are not authorized for this command"
            await context.send(embed=reply)
            return

        commands = context.message.content.split(' ')
        if len(commands) > 1:
            self.__flagNewSong = context.message.content

        await context.send(embed=reply)

        if context.bot.channel != None:
            voice_channel = context.bot.channel

            songFolder = os.path.join(self.bot.configuration[constants.CONF_REPOSITORY_PATH], constants.STR_SUBDIR_DOWNLOADS)

            while not self.__flagStop:

                if self.__flagNewSong:
                    songName = SearchSong(songFolder, self.__flagNewSong)
                    self.__flagNewSong = None
                else:
                    songName = ShufflePlaylist(songFolder)

                if voice_channel.is_playing():
                    voice_channel.stop()

                voice_channel.play(discord.FFmpegPCMAudio(os.path.join(songFolder, songName)),
                                   after=lambda e: print('done', e))

                while voice_channel.is_playing():
                    await self.bot.change_presence(activity=discord.Game(f"Playing... {songName[:-4]}"))
                    await asyncio.sleep(1)

                    if self.__flagStop or self.__flagNewSong:
                        break

            voice_channel.stop()
            self.__flagStop = False

    @commands.hybrid_command(name="playlist", description="List all songs.")
    async def listSongs(self, context: Context) -> None:
        reply = discord.Embed(description="")

        if not IsUser(self.bot, context):
            reply.description = "You are not authorized for this command"
            await context.send(embed=reply)
            return

        list: dict = self.bot.dbManager.ReadSongs()
        for key in list:
            reply.description += list[key] + "\n"

        await context.send(embed=reply)

    @ commands.hybrid_command(name="stop", description="Starts playing music.")
    async def stopMusic(self, context: Context) -> None:
        if not IsUser(self.bot, context):
            reply.description = "You are not authorized for this command"
            await context.send(embed=reply)
            return

        self.__flagStop = True
        reply = discord.Embed(description="Stop request has been sent")

        await context.send(embed=reply)


async def setup(bot) -> None:
    await bot.add_cog(Player(bot))


def IsUser(bot, context: Context) -> bool:
    username = context.author.name + "#" + context.author.discriminator
    result = bot.dbManager.IsUser(username)

    return result


def IsYoutubeUrl(url: str) -> bool:
    url = url.lower()
    pattern = re.compile(constants.PATTERN_YOUTUBE_URL)

    if pattern.match(url):
        return True

    return False


def DownloadFromYoutube(url: str, configuration: dict, logger: Logger) -> tuple:
    repositoryPath = os.path.join(configuration[constants.CONF_REPOSITORY_PATH], constants.STR_SUBDIR_DOWNLOADS)
    cookiesPath = os.path.join(configuration[constants.CONF_REPOSITORY_PATH], constants.STR_COOKIES_FILE)

    if not os.path.exists(repositoryPath):
        os.makedirs(repositoryPath)

    options = {
        'quiet': True,
        'logger': logger,
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'download_archive': os.path.join(repositoryPath, constants.STR_YOUTUBEDL_ARCHIVE_FILE),
        'match_filter': DownloadFilter
    }

    if os.path.exists(cookiesPath):
        options['cookies'] = cookiesPath
    elif constants.CONF_COOKIES_FROM_BROWSER in configuration:
        options['cookies_from_browser'] = configuration[constants.CONF_COOKIES_FROM_BROWSER]

    with YoutubeDL(options) as ytdl:
        videoInfo = ytdl.extract_info(url, download=False)

    songTitle = videoInfo.get('title', None)
    options['outtmpl'] = os.path.join(repositoryPath, songTitle)
    song: tuple = (songTitle, url)

    with YoutubeDL(options) as ytdl:
        ytdl.download([url])

    return song


def DownloadFilter(info, *, incomplete):
    duration = info.get('duration')

    if duration and duration > 10 * 60:
        return 'Video is too long'

    if duration and duration < 1 * 60:
        return 'Video is too short'


def ShufflePlaylist(folder: str) -> str:
    songs = []

    for file in os.listdir(folder):
        if file.endswith('.mp3'):
            songs.append(file)

    randomizer = random.randint(0, len(songs) - 1)

    return songs[randomizer]


def SearchSong(folder: str, songHint: str) -> str:
    songs = []
    rankedSongs = {}

    for file in os.listdir(folder):
        if file.endswith('.mp3'):
            rankedSongs[file] = 0
            songs.append(file)

    keywords = songHint.replace("!play ", "").split(' ')

    for song in songs:
        for keyword in keywords:
            if keyword.lower() in str(song).lower():
                rankedSongs[song] += 1

    result = max(rankedSongs, key=lambda x: rankedSongs[x])

    return result
