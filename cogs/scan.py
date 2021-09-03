import sys
import traceback
from datetime import datetime
import time, timeago

import discord
from discord.ext import commands
import asyncio

import Bot
from Bot import EMOJI_ERROR, EMOJI_OK_BOX, EMOJI_OK_HAND, EMOJI_INFORMATION, logchanbot
from config import config


class Scan(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(ban_members=True)
    @commands.command(usage='scanname', aliases=['scannick'], description="Scan similar name")
    async def scanname(self, ctx, contain: str, option: str=None):
        if len(contain) < 3:
            await ctx.send(f'{ctx.author.mention} criteria too short.')
            return

        # scan any name of user contains
        count = 0
        user_found_id = []
        names_ids = []
        try:
            listMembers = [member for member in ctx.guild.members if member.bot == False]
            if option and (option.upper() == "KICK") and len(listMembers) >= config.discord.max_kick:
                # Ignore for member bigger than 10, dangerous
                await ctx.send(f'{ctx.author.mention} There are more than **{config.discord.max_kick}** users to remove. KICK halted. I will list only their names.')
                option = None
            for member in listMembers:
                if member.bot == False:
                    name = member.name
                    if member.nick:
                        name = member.nick
                    if contain.upper() in name.upper():
                        user_found_id.append(member.id)
                        names_ids.append("{}, {}, {}#{}, joined_at: {}".format(member.id, name, member.name, member.discriminator, member.joined_at.strftime("%d-%b-%Y")))
                        count += 1
            if count > 0:
                name_list = "\n".join(names_ids)
                await ctx.send(f'{ctx.author.mention} Found {str(count)} user(s) contains `{contain}`. ```{name_list}```')
                if option and option.upper() in ["KICK", "BAN"]:
                    botLogChan = self.bot.get_channel(id=int(config.discord.logchan))
                    number_kick_ban = 0
                    for member in listMembers:
                        name = member.name
                        if member.nick:
                            name = member.nick
                        if contain.upper() in name.upper():
                            # If there is option
                            EMOJI_KICK = "\U0001F528"
                            EMOJI_BAN = "\U0001F6AB"
                            EMOJI_SKIP = "\u23ED"
                            EMOJI_STOP = "\U0001F6D1"
                            embed = discord.Embed(title=f'{member.name}#{member.discriminator} / Name: {name}', description=f'Warning user ID: {member.id}',
                                                  timestamp=datetime.utcnow())
                            embed.add_field(name="Highest role", value=member.top_role, inline=False)
                            embed.add_field(name="Joined", value=str(member.joined_at.strftime("%d-%b-%Y") + ': ' + timeago.format(member.joined_at, datetime.utcnow())), inline=False)
                            embed.add_field(name="Created", value=str(member.created_at.strftime("%d-%b-%Y") + ': ' + timeago.format(member.created_at, datetime.utcnow())), inline=False)
                            if option.upper() == "KICK":
                                embed.set_footer(text=f"Re-act {EMOJI_KICK}: KICK, {EMOJI_SKIP}: SKIP, {EMOJI_STOP}: EXIT, timeout 15s")
                            elif option.upper() == "BAN":
                                embed.set_footer(text=f"Re-act {EMOJI_BAN}: BAN, {EMOJI_SKIP}: SKIP, {EMOJI_STOP}: EXIT, timeout 15s")
                            embed.set_thumbnail(url=member.avatar_url)
                            try:
                                msg = await ctx.send(embed=embed)
                                if option.upper() == "KICK":
                                    await msg.add_reaction(EMOJI_KICK)
                                elif option.upper() == "BAN":
                                    await msg.add_reaction(EMOJI_BAN)
                                await msg.add_reaction(EMOJI_SKIP)
                                await msg.add_reaction(EMOJI_STOP)
                                completed_each = False
                                
                                def check(reaction, user):
                                    return user == ctx.message.author and reaction.message.author == self.bot.user and reaction.message.id == msg.id
                                while completed_each == False:
                                    try:
                                        reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=check)
                                    except asyncio.TimeoutError:
                                        await ctx.send(f'{ctx.author.mention} Time-out.')
                                        completed_each = True
                                        break
                                    if reaction.emoji and str(reaction.emoji) == EMOJI_KICK:
                                        # Let's start to kick
                                        try:
                                            try:
                                                await member.send(f'You are kicked from {ctx.guild.name}.')
                                            except Exception as e:
                                                pass
                                            await member.guild.kick(member)
                                            number_kick_ban += 1
                                            completed_each = True
                                            await botLogChan.send(f"I executed `kick` on behalf of {ctx.author.name} => {EMOJI_KICK} {member.name}#{member.discriminator} / Name: {name} / {member.id}")
                                        except Exception as e:
                                            print(traceback.format_exc())
                                            await ctx.send(f'{ctx.author.mention} Error removing {member.name}#{member.discriminator} / {member.id}.')
                                        continue
                                    elif reaction.emoji and str(reaction.emoji) == EMOJI_BAN:
                                        # Let's start to kick
                                        try:
                                            try:
                                                await member.send(f'You are banned from {ctx.guild.name}.')
                                            except Exception as e:
                                                pass
                                            await member.guild.ban(user=member, reason=f'You are banned from {ctx.guild.name}.')
                                            number_kick_ban += 1
                                            completed_each = True
                                            await botLogChan.send(f"I executed `ban` on behalf of {ctx.author.name} => {EMOJI_BAN} {member.name}#{member.discriminator} / Name: {name} / {member.id}")
                                        except Exception as e:
                                            print(traceback.format_exc())
                                            await ctx.send(f'{ctx.author.mention} Error banning {member.name}#{member.discriminator} / {member.id}.')
                                        continue
                                    elif reaction.emoji and str(reaction.emoji) == EMOJI_SKIP:
                                        # Stop all que
                                        await ctx.send(f'{ctx.author.mention} OK, skipped this {member.name}#{member.discriminator} / {member.id}.')
                                        completed_each = True
                                        break
                                    elif reaction.emoji and str(reaction.emoji) == EMOJI_STOP:
                                        # Stop all que
                                        await ctx.send(f'{ctx.author.mention} OK, stopped all processes. Total kicked: **{str(number_kick_ban)}**')
                                        completed_each = True
                                        return
                                continue
                            except Exception as e:
                                continue
                                print(traceback.format_exc())
                    if number_kick_ban > 0:
                        await ctx.send(f'{ctx.author.mention} Finished all processes. Total kicked/ban: **{str(number_kick_ban)}**')
            else:
                await ctx.send(f'{ctx.author.mention} Found 0 user(s) contains `{contain}`.')
        except Exception as e:
            print(traceback.format_exc())


def setup(bot):
    bot.add_cog(Scan(bot))
