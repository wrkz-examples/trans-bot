import json
import sys
import time
import traceback

import discord
from discord.ext import commands
from googletrans import Translator
from datetime import datetime
import Bot
from config import config

FROM_CHANNELS = [int(chan) for chan in config.trans.channels.split(",")]
TO_CHANNELS = [int(chan) for chan in config.trans.to_channels.split(",")]

class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        botLogChan = self.bot.get_channel(id=int(config.discord.logchan))
        if before.nick != after.nick:
            if after.nick is None:
                await botLogChan.send(f'{before.id}: {before.name} changes **nick** to default nick.')
            else:
                await botLogChan.send(f'{before.id}: {before.name} changes **nick** to **{after.nick}**')


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        return

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        return

    @commands.Cog.listener()
    async def on_member_join(self, member):
        botLogChan = self.bot.get_channel(id=int(config.discord.logchan))
        account_created = member.created_at
        account_joined = member.joined_at
        if (datetime.utcnow() - account_created).total_seconds() >= 7200:
            to_send = '{0.mention} (`{1.id}`) has joined {2.name}!'.format(member, member, member.guild)
        else:
            to_send = '{0.mention} (`{1.id}`) has joined {2.name}! **Warning!!!**, {3.mention} just created his/her account less than 2hr.'.format(member, member, member.guild, member)
        await botLogChan.send(to_send)
        return


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        botLogChan = self.bot.get_channel(id=int(config.discord.logchan))
        to_send = '{0.mention} (`{1.name}`) has left {2.name}!'.format(member, member, member.guild)
        await botLogChan.send(to_send)


    @commands.Cog.listener()
    async def on_message(self, message):
        # should ignore webhook message
        if isinstance(message.channel, discord.DMChannel) == False and message.webhook_id:
            return
        # Ignore bot message too
        if message.author.bot == True:
            return
        botLogChan = self.bot.get_channel(id=int(config.discord.logchan))
        
        # If in channels:
        if message.channel.id in FROM_CHANNELS:
            to_channel_id = FROM_CHANNELS.index(message.channel.id)
            channel = self.bot.get_channel(id=TO_CHANNELS[to_channel_id])
            # channel = self.bot.get_channel(id=config.discord.logchan)
            if channel:
                def user_translated(text):
                    translator = Translator()
                    translated = translator.translate(text, dest='en')
                    return {'original': text, 'translated': translated.text, 'src_lang': translated.src}
                try:
                    translated = user_translated(message.content)
                    if translated:
                       await channel.send("{}: {}#{}/{}: {}".format(message.channel.mention, message.author.name, message.author.discriminator, message.author.id, translated['translated']))
                except Exception as e:
                    traceback.print_exc(file=sys.stdout)
            else:
                msg = await botLogChan.send("Can not find channel ID: {}".format(to_channel_id))


def setup(bot):
    bot.add_cog(Events(bot))
