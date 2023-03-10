import discord
from discord.ext import commands
from discord.ext.commands import Context

from constants import *


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="List all commands the bot has loaded.")
    async def sendHelp(self, context: Context) -> None:
        prefix = self.bot.configuration[CONF_PREFIX]
        embed = discord.Embed(
            title="Help", description="List of available commands:"
        )

        for i in self.bot.cogs:
            cog = self.bot.get_cog(i.lower())
            commands = cog.get_commands()
            data = []
            for command in commands:
                description = command.description.partition('\n')[0]
                data.append(f"{prefix}{command.name} - {description}")

            help_text = "\n".join(data)
            embed.add_field(name=i.capitalize(),
                            value=f'```{help_text}```', inline=False)

        await context.send(embed=embed)

    @commands.hybrid_command(name="adduser", description="Adds a user to the system. Only for admins")
    async def addUser(self, context: Context) -> None:
        reply = discord.Embed(description="")

        if not IsAdmin(self.bot, context):
            reply.description = "You are not authorized for this command"
            await context.send(embed=reply)
            return

        command = context.message.content.split(' ')
        if len(command) != 2:
            reply.description = "To use the command, you must include a discord name with discriminator: user#123"
            await context.send(embed=reply)
            return

        AddUser(self.bot, context)
        reply.description = "User has been added"

        await context.send(embed=reply)


async def setup(bot):
    await bot.add_cog(General(bot))


def IsAdmin(bot, context: Context) -> bool:
    username = context.author.name + "#" + context.author.discriminator
    result = bot.dbManager.IsAdmin(username)

    return result


def IsUser(bot, context: Context) -> bool:
    username = context.author.name + "#" + context.author.discriminator
    result = bot.dbManager.IsUser(username)

    return result


def AddUser(bot, context: Context) -> None:
    username = context.author.name + "#" + context.author.discriminator
    bot.dbManager.InsertUser(username)
