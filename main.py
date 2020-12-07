import discord
from discord.ext import commands
import os
from keep_alive import keep_alive
import time
import platform
from Utils.mongo import Document
import motor.motor_asyncio
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


#get prefix for a server
async def get_prefix(bot, message):
    if not message.guild:
        return "b!"
    else:
        prefix = await bot.prefixes.find(message.guild.id)
        if prefix:
            return prefix["prefix"]
        else:
            return "b!"


bot = commands.Bot(command_prefix=get_prefix, case_insensitive=False)


#handles the module enable/disable thing
@bot.check
async def canBeRun(ctx):
    defaultCogs = [
        'BotOwnerCommands', 'CoreCommands', 'ErrorHandler', 'ModuleInstaller'
    ]
    guild = ctx.guild
    if guild:
        cog = ctx.command.cog
        if cog == None:
            return True
        else:
            modules = await bot.enabledModules.find(guild.id)
            modules = modules["modules"]
            if cog.qualified_name in defaultCogs or cog.qualified_name in modules:
                return True
            else:
                return False
    else:
        return True


#On Ready
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="b!help"))

    print("Setting bot info values")
    #set some values for the botinfo command
    bot.startTime = time.time()
    bot.botVersion = '0.1.0'
    bot.pythonVersion = platform.python_version()
    bot.dpyVersion = discord.__version__
    bot.developer = 'Kosmic#1337'

    print("Initializing Database")
    #initialize database
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_url))
    bot.db = bot.mongo["SentientAnomaly"]
    bot.prefixes = Document(bot.db, "prefixes")
    bot.enabledModules = Document(bot.db, "enabledModules")
    bot.curseFilterModule = Document(bot.db, "curseFilterModule")

    print("Cleaning Up Database")
    #clean up the database
    guildList = [guild.id for guild in bot.guilds]

    #prefixes database
    prefixes = await bot.prefixes.get_all()
    guildsInPrefixDB = [guild.get('_id') for guild in prefixes]
    for guild in guildList:
        if guild not in guildsInPrefixDB:
            await bot.prefixes.upsert({"_id": guild, "prefix": 'b!'})
    for guild in guildsInPrefixDB:
        if guild not in guildList:
            await bot.prefixes.delete_by_id(guild)

    #enabledModules database
    enabledModules = await bot.enabledModules.get_all()
    guildsInEnabledModulesDB = [guild.get('_id') for guild in enabledModules]
    for guild in guildList:
        if guild not in guildsInEnabledModulesDB:
            await bot.enabledModules.upsert({"_id": guild, "modules": []})
    for guild in guildsInEnabledModulesDB:
        if guild not in guildList:
            await bot.enabledModules.delete_by_id(guild)

    #curseFilterModule database
    enabledModules = await bot.curseFilterModule.get_all()
    guildsInCurseFilterDB = [guild.get('_id') for guild in enabledModules]
    for guild in guildList:
        if guild not in guildsInCurseFilterDB:
            await bot.curseFilterModule.upsert({"_id": guild, "filters": []})
    for guild in guildsInCurseFilterDB:
        if guild not in guildList:
            await bot.curseFilterModule.delete_by_id(guild)

    print(bot.user, "has booted up successfully.")


#database building for a new server
@bot.event
async def on_guild_join(guild):
    print(f"Joined guild {guild}. Setting up database for that guild.")
    await bot.prefixes.upsert({"_id": guild.id, "prefix": 'b!'})
    await bot.enabledModules.upsert({"_id": guild.id, 'modules': []})
    await bot.curseFilterModule.upsert({"_id": guild.id, "filters": []})

#database cleanup when the bot leaves
@bot.event
async def on_guild_remove(guild):
    print(f"Left guild {guild}. Cleaning up database for that guild.")
    await bot.prefixes.delete_by_id(guild.id)
    await bot.enabledModules.delete_by_id(guild.id)
    await bot.curseFilterModule.delete_by_id(guild.id)

#check to see if the bot was mentioned
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if '<@!780149307978416138>' == message.content or '<@780149307978416138>' == message.content:
        prefix = await bot.command_prefix(bot, message)
        await message.channel.send(f'My prefix is `{prefix}`.')
    await bot.process_commands(message)


#load Core Functions
for filename in os.listdir('./CoreFunctions'):
    if filename.endswith('.py'):
        bot.load_extension(f'CoreFunctions.{filename[:-3]}')
        print(f'Loaded Core Function: {filename[:-3]}')

#load Modules
bot.loadedModules = []
for filename in os.listdir('./Modules'):
    if filename.endswith('.py'):
        bot.load_extension(f'Modules.{filename[:-3]}')
        bot.loadedModules.append(filename[:-3])
        print(f'Loaded Module: {filename[:-3]}')

keep_alive()
bot.token = os.environ.get("DISCORD_BOT_TOKEN")
bot.connection_url = os.environ.get("MONGO")
bot.run(bot.token)
