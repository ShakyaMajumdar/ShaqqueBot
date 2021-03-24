import discord
from discord.ext import commands


def is_bot_author():
    async def predicate(ctx: commands.Context):
        return ctx.author.id == 787351231332483102

    return commands.check(predicate)


class Miscellaneous(commands.Cog):
    """Miscellaneous stuff."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx: commands.Context) -> None:
        """Simple test command to check if bot is working"""
        await ctx.send("Bot online.")

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """Send bot ping"""
        await ctx.send(f"Pong! {round(self.bot.latency, 2)} ms")

    @commands.command(pass_context=False)
    @is_bot_author()
    async def echo(
        self, channel: discord.TextChannel, message_id: int, *, reply_message: str
    ):
        message = await channel.fetch_message(message_id)
        await message.reply(reply_message)


def setup(bot: commands.Bot) -> None:
    """Load Miscellaneous Cog"""
    bot.add_cog(Miscellaneous(bot))
