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


class Addrole(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(usage="rolecount [role]", description="Counts the number of people who have a role, If no role is specified it counts everyone.")
    async def rolecount(self, ctx, *, role: discord.Role = None):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send('This command can not be in private.')
            return
        if not role:
            name = " the server"
            nmembers = ctx.guild.member_count
            color = discord.Color.gold()
        else:
            name = role.name
            nmembers = len(role.members)
            color = role.color
        try:
            embed = discord.Embed(color=color).add_field(name=f"Members in {name}", value=f"{nmembers:,}")
            await ctx.send(embed=embed)
        except Exception as e:
            print(traceback.format_exc())


    @commands.has_permissions(ban_members=True)
    @commands.command(usage='addrole', aliases=['addroles'], description="Add everyone to a specific role")
    async def addrole(self, ctx, rolename: str):
        allowed_roles = config.discord.allowed_roles.split(",")
        if rolename.upper() not in [role.upper() for role in allowed_roles]:
            await ctx.send(f'{ctx.author.mention} Invalid given role or not defined in setting.')
            return

        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send(f'{EMOJI_ERROR} {ctx.author.mention} This command can not be in private.')
            return

        get_guild = self.bot.get_guild(id=config.discord.bao_guild)
        if config.discord.bao_guild != ctx.guild.id:
            await ctx.send(f'{EMOJI_ERROR} {ctx.author.mention} Please config guild ID properly.')
            return

        num_verified = 0
        skipped_user = 0
        get_verified_role = discord.utils.get(get_guild.roles, name=rolename)
        botLogChan = self.bot.get_channel(id=int(config.discord.logchan))
        try:
            if get_verified_role:
                # let's loop everyone and check if they have that role. If not, add it.
                try:
                    for member in ctx.guild.members:
                        if get_verified_role not in member.roles:
                            # add him
                            await member.add_roles(get_verified_role)
                            num_verified += 1
                        else:
                            skipped_user += 1
                except Exception as e:
                    print(traceback.format_exc())
                    await botLogChan.send(traceback.format_exc())
                await botLogChan.send(f'Addrole completed for `{rolename}`. Added role to number of users: `{str(num_verified)}`. Skipped users: `{str(skipped_user)}`. Executed by `{ctx.author.name}#{ctx.author.discriminator} / {ctx.author.id}`')

                await ctx.send(f'{ctx.author.mention} Addrole completed for `{rolename}`. Added role to number of users: `{str(num_verified)}`. Skipped users: `{str(skipped_user)}`.')
                return
            else:
                await ctx.send(f'{ctx.author.mention} can not find `{rolename}`.')
        except discord.errors.Forbidden as e:
            await botLogChan.send(f'Add role incomplete: I have not sufficient permission. Executed by `{ctx.author.name}#{ctx.author.discriminator} / {ctx.author.id}`')
        except Exception as e:
            print(traceback.format_exc())
            


def setup(bot):
    bot.add_cog(Addrole(bot))
