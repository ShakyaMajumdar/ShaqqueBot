from typing import Union, Optional

import discord
from discord.ext import commands

NUMBER_EMOJIS = {
    1: ":one:",
    2: ":two:",
    3: ":three:",
    4: ":four:",
    5: ":five:",
    6: ":six:",
    7: ":seven:",
    8: ":eight:",
    9: ":nine:"
}


class TicTacToe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._reset_game()

    def _reset_game(self):
        self.game_in_play = False

        self.board: list[list[Union[int, str]]] = [[3 * i + 1, 3 * i + 2, 3 * i + 3] for i in range(3)]
        self.empty_spots: set[int] = set(range(1, 10))

        self.naught_player: Optional[discord.Member] = None
        self.cross_player: Optional[discord.Member] = None

        self.next_turn: Optional[tuple[str, str]] = None

        self.board_embed_message: Optional[discord.Message] = None

    def _get_board_embed(self):
        s = ""
        for r in self.board:
            for c in r:
                if isinstance(c, int):
                    s += NUMBER_EMOJIS[c]
                elif c == "O":
                    s += ":o:"
                else:
                    s += ":x:"
            s += "\n"

        embed = discord.Embed(description=s)
        return embed

    @commands.command(name="ttt")
    async def start(self, ctx: commands.Context, member: discord.Member = None):

        """if member == ctx.author:
            raise commands.UserInputError('You can\'t play with yourself.')"""

        self.game_in_play = True

        self.cross_player = ctx.author
        self.naught_player = member

        self.next_turn = self.cross_player, "X"

        embed_message = await ctx.send(embed=self._get_board_embed())
        self.board_embed_message = embed_message

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, player: discord.Member):

        if not self.game_in_play or reaction.message != self.board_embed_message or player != self.next_turn[0]:
            return

        try:
            pos = int(str(reaction.emoji)[0])
        except ValueError:
            return

        if pos in self.empty_spots:
            self.empty_spots.remove(pos)
        else:
            return

        self.board[(pos-1) // 3][(pos-1) % 3] = self.next_turn[1]

        await self.board_embed_message.edit(embed=self._get_board_embed())

        self.next_turn = (self.cross_player, "X") if self.next_turn[1] == "O" else (self.naught_player, "O")

        status = self._get_game_status()

        if status == "in progress":
            return
        elif status == "X":
            await self.board_embed_message.channel.send(f"{self.cross_player.mention} has won the game!")
        elif status == "O":
            await self.board_embed_message.channel.send(f"{self.naught_player.mention} has won the game!")
        else:
            await self.board_embed_message.channel.send(f"Game ended in a draw!")

        self._reset_game()

    def _get_game_status(self):
        if self._has_won("O"):
            return "O"
        if self._has_won("X"):
            return "X"

        if not self.empty_spots:
            return "draw"

        return "in progress"

    def _has_won(self, piece: str):

        for row in self.board:
            if row.count(piece) == 3:
                return True

        for col in zip(*self.board):
            if col.count(piece) == 3:
                return True

        wins_left_diagonal = True
        wins_right_diagonal = True

        for i, row in enumerate(self.board):
            for j, item in enumerate(row):
                if i == j and item != piece:
                    wins_left_diagonal = False

                if i+j == 2 and item != piece:
                    wins_right_diagonal = False

        return any((wins_left_diagonal, wins_right_diagonal))


def setup(bot: commands.Bot):
    """Add TicTacToe Cog"""
    bot.add_cog(TicTacToe(bot))
