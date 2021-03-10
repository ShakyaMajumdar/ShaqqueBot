import datetime
from typing import Union, Optional

import discord
from discord.ext import commands, tasks

NUMBER_EMOJIS = {i: f"{i}\N{COMBINING ENCLOSING KEYCAP}" for i in range(1, 10)}

MOVE_TIME_LIMIT = 20


class TicTacToe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._reset_game()

    def _reset_game(self):
        self.game_in_play = False

        self.board: list[list[Union[int, str]]] = [
            [3 * i + 1, 3 * i + 2, 3 * i + 3] for i in range(3)
        ]
        self.empty_spots: set[int] = set(range(1, 10))

        self.naught_player: Optional[discord.Member] = None
        self.cross_player: Optional[discord.Member] = None

        self.next_turn: Optional[tuple[str, str]] = None

        self.board_embed_message: Optional[discord.Message] = None

        self.last_move_timestamp = None

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

        if self.game_in_play:
            await ctx.send("One game is already in progress!")
            return

        """if member == ctx.author:
            raise commands.UserInputError('You can\'t play with yourself.')"""

        self.game_in_play = True

        self.cross_player = ctx.author
        self.naught_player = member

        self.next_turn = self.cross_player, "X"

        embed_message = await ctx.send(
            content=f"It's your turn now, {self.next_turn[0].mention}!",
            embed=self._get_board_embed(),
        )
        self.board_embed_message = embed_message

        for emoji in NUMBER_EMOJIS.values():
            await embed_message.add_reaction(emoji)

        self.last_move_timestamp = datetime.datetime.now()
        self._check_time_out.start()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, player: discord.Member):

        self.last_move_timestamp = datetime.datetime.now()

        if player == self.bot.user:
            return

        # await reaction.remove(player)

        if (
            not self.game_in_play
            or reaction.message != self.board_embed_message
            or player != self.next_turn[0]
        ):
            return

        try:
            pos = int(str(reaction.emoji)[0])
        except ValueError:
            return

        if pos in self.empty_spots:
            self.empty_spots.remove(pos)
        else:
            return

        await reaction.remove(self.bot.user)

        self.board[(pos - 1) // 3][(pos - 1) % 3] = self.next_turn[1]

        self.next_turn = (
            (self.cross_player, "X")
            if self.next_turn[1] == "O"
            else (self.naught_player, "O")
        )

        await self.board_embed_message.edit(
            content=f"It's your turn now, {self.next_turn[0].mention}!",
            embed=self._get_board_embed(),
        )

        status = self._get_game_status()

        if status == "in progress":
            return
        elif status == "X":
            await self.board_embed_message.channel.send(
                f"{self.cross_player.mention} has won the game!"
            )
        elif status == "O":
            await self.board_embed_message.channel.send(
                f"{self.naught_player.mention} has won the game!"
            )
        else:
            await self.board_embed_message.channel.send("Game ended in a draw!")

        self._check_time_out.cancel()
        # await self.board_embed_message.clear_reactions()
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

                if i + j == 2 and item != piece:
                    wins_right_diagonal = False

        return any((wins_left_diagonal, wins_right_diagonal))

    @tasks.loop(seconds=1)
    async def _check_time_out(self):
        if not self.game_in_play:
            return
        lapsed = datetime.datetime.now() - self.last_move_timestamp
        if lapsed.seconds > MOVE_TIME_LIMIT:
            await self.board_embed_message.channel.send(
                f"{self.next_turn[0].mention} your time is up! Ending game now."
            )
            self._check_time_out.cancel()
            # await self.board_embed_message.clear_reactions()
            self._reset_game()
        elif lapsed.seconds == MOVE_TIME_LIMIT - 5:
            await self.board_embed_message.channel.send(
                f"Hurry up {self.next_turn[0].mention}! You have 5 seconds remaining."
            )


def setup(bot: commands.Bot):
    """Add TicTacToe Cog"""
    bot.add_cog(TicTacToe(bot))
