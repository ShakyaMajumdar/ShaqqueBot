from discord.ext import commands


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


def setup(bot: commands.Bot) -> None:
    """Load Miscellaneous Cog"""
    bot.add_cog(Miscellaneous(bot))
