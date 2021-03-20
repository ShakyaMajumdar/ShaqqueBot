import discord
from discord.ext import commands


class Avatar(commands.Cog):
    """Cog for getting members' avatars"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def avatar(
        self, ctx: commands.Context, member: discord.Member = None
    ) -> None:
        member = member or ctx.author
        avatar = member.avatar_url
        await ctx.send(avatar)


def setup(bot: commands.Bot) -> None:
    """Load the Avatar cog."""
    bot.add_cog(Avatar(bot))
