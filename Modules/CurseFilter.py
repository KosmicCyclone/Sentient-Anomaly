import discord
from discord.ext import commands
import re

#Open list of curses
with open("BadWords/cussWords.txt") as cussWordslist:
    cussWords = [
        cussWord.lower().replace('\n', '').replace('\t', '')
        for cussWord in cussWordslist.readlines()
    ]
with open("BadWords/discriminatoryWords.txt") as discriminatoryWordsList:
    discriminatoryWords = [
        discriminatoryWord.lower().replace('\n', '').replace('\t', '')
        for discriminatoryWord in discriminatoryWordsList.readlines()
    ]
with open("BadWords/vulgarWords.txt") as vulgarWordsList:
    vulgarWords = [
        vulgarWord.lower().replace('\n', '').replace('\t', '')
        for vulgarWord in vulgarWordsList.readlines()
    ]


class CurseFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Profanity Filter
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        settings = await self.bot.curseFilterModule.find(message.guild.id)
        settings = settings['filters']

        message_content = message.content.strip().lower()
        message_content = re.split('[^a-zA-Z]', message_content)

        if "Cuss" in settings:
            if any(bad_word in message_content for bad_word in cussWords):
                await message.channel.send(
                    f'{message.author.mention} watch your language, you f||or||king ||ice||hole.',
                    delete_after=7)
                await message.delete()
                return
        if "Vulgar" in settings:
            if any(bad_word in message_content for bad_word in vulgarWords):
                await message.channel.send(
                    f'{message.author.mention} watch your language, you f||or||king ||ice||hole.',
                    delete_after=7)
                await message.delete()
                return
        if "Discriminatory" in settings:
            if any(bad_word in message_content
                   for bad_word in discriminatoryWords):
                await message.channel.send(
                    f'{message.author.mention} watch your language, you f||or||king ||ice||hole.',
                    delete_after=7)
                await message.delete()
                return

    @commands.command(
        aliases=['cursetoggle'],
        brief='Curse filter settings',
        description=
        'Toggles various curse filters (Cuss/Vulgar/Discriminatory) on and off'
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cursefiltertoggle(self, ctx, filter: str = None):
        if filter == None or filter not in [
                'Cuss', 'Vulgar', 'Discriminatory'
        ]:
            await ctx.send(
                'Please specify which of the following curse filters you want to toggle:\nCuss\nVulgar\nDiscriminatory'
            )
        else:
            async with ctx.typing():
                settings = await self.bot.curseFilterModule.find(ctx.guild.id)
                settings = settings['filters']
            if filter in settings:
                await ctx.send(f'Toggled {filter} off')
                settings.remove(filter)
            else:
                await ctx.send(f'Toggled {filter} on')
                settings.append(filter)
            await self.bot.curseFilterModule.upsert({
                "_id": ctx.guild.id,
                "filters": settings
            })


def setup(bot):
    bot.add_cog(CurseFilter(bot))
