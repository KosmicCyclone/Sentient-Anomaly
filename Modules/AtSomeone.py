import discord
from discord.ext import commands
import random


class AtSomeone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @commands.has_permissions(mention_everyone=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def on_message(self, message):
        if message.author.bot:
            return
        if '@someone' in message.content:
            channel = message.channel
            async with channel.typing():
                ViewableMembers = channel.members
                someone = random.choice(ViewableMembers)
            await message.channel.send(someone.mention)


def setup(bot):
    bot.add_cog(AtSomeone(bot))
