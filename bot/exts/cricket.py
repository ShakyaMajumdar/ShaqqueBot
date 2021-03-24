from dataclasses import dataclass
# from pprint import pprint

import aiohttp
import discord
from discord.ext import commands

from bot import constants

API_URL = "https://livescore6.p.rapidapi.com/matches/v2/"
LIVE_MATCHES_URL = API_URL + "list-live"

HEADERS = {
    "x-rapidapi-key": constants.RAPIDAPI_KEY,
    "x-rapidapi-host": constants.RAPIDAPI_LIVESCORE6_HOST,
}


@dataclass
class CricketMatch:
    format: str
    match_no: str
    teams: tuple[str, str]
    summary: str
    scores: dict
    status: str
    _eid: str


class Cricket(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def get_live_matches_list_embed(matches: list[CricketMatch]) -> discord.Embed:
        embed = discord.Embed(title="Current Live Matches:", colour=discord.Colour.random())

        for match in matches:
            match_info = f"""\
{match.teams[0]}: {match.scores['T1I1']} 
{match.teams[1]}: {match.scores['T2I1']}
"""
            if "test" in match.format.lower():
                match_info += f"""\
{match.teams[0]}: {match.scores['T1I2']}
{match.teams[1]}: {match.scores['T2I2']}
"""
            match_info += f"""\

{match.summary}
{match.status}
"""
            embed.add_field(
                name="{} vs {}: {}".format(*match.teams, match.match_no or match.format), value=match_info, inline=False
            )
        return embed

    @commands.command()
    async def live_scores(self, ctx: commands.Context) -> None:
        """Sends information about ongoing cricket matches."""

        querystring = {"Category": "cricket"}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                LIVE_MATCHES_URL, headers=HEADERS, params=querystring
            ) as response:
                response = await response.json()
                # pprint(response)
                if not response:
                    await ctx.send("No matches in progress currently!")
                    return

                matches = [
                    CricketMatch(
                        format=match["EtTx"],
                        teams=(
                            match["T1"][0]["Nm"],
                            match["T2"][0]["Nm"],
                        ),
                        summary=match["ECo"],
                        _eid=match["Eid"],
                        status=match["EpsL"],
                        scores={
                            "T1I1": f"{match.get('Tr1C1', '-')}/"
                            f"{match.get('Tr1CW1', '-')} "
                            f"({match.get('Tr1CO1', '-')})",
                            "T2I1": f"{match.get('Tr2C1', '-')}/"
                            f"{match.get('Tr2CW1', '-')} "
                            f"({match.get('Tr2CO1', '-')})",
                            "T1I2": f"{match.get('Tr1C2', '-')}/"
                            f"{match.get('Tr1CW2', '-')} "
                            f"({match.get('Tr1CO2', '-')})",
                            "T2I2": f"{match.get('Tr2C2', '-')}/"
                            f"{match.get('Tr2CW2', '-')} "
                            f"({match.get('Tr2CO2', '-')})",
                        },
                        match_no=match.get("ErnInf", ""),
                    )
                    for match in map(lambda m: m["Events"][0], response["Stages"])
                ]

        await ctx.send(embed=self.get_live_matches_list_embed(matches))


def setup(bot: commands.Bot):
    """Add Cricket Cog."""
    bot.add_cog(Cricket(bot))
