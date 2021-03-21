import datetime
import itertools
from typing import Union, Optional

import discord
from discord.ext import commands, tasks

NUMBER_EMOJIS = {i: f"{i}\N{COMBINING ENCLOSING KEYCAP}" for i in range(1, 10)}

MOVE_TIME_LIMIT = 20


class Game:
    def __init__(self, cross_player: discord.Member, naught_player: discord.Member):

        self.players = {"X": cross_player, "O": naught_player}

        self.next_turn_toggler = itertools.cycle(self.players.items()).__next__
        self.next_turn: tuple[str, discord.Member] = self.next_turn_toggler()

        self.board: list[list[Union[int, str]]] = [
            [3 * i + 1, 3 * i + 2, 3 * i + 3] for i in range(3)
        ]

        self.empty_spots: set[int] = set(range(1, 10))

        self.embed_message: Optional[discord.Message] = None

        self.last_move_timestamp: datetime.datetime = datetime.datetime.now()

    def get_board_embed(self) -> discord.Embed:
        """Get embed representing current board."""
        board_str = ""
        for row in self.board:
            for col in row:
                if isinstance(col, int):
                    board_str += NUMBER_EMOJIS[col]
                elif col == "O":
                    board_str += ":o:"
                else:
                    board_str += ":x:"
            board_str += "\n"

        embed = discord.Embed(description=board_str)
        return embed

    def _get_game_status(self) -> str:
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

        for i in range(3):
            if self.board[i][i] != piece:
                wins_left_diagonal = False
            if self.board[i][2 - i] != piece:
                wins_right_diagonal = False

        return wins_left_diagonal or wins_right_diagonal

    async def update(self, player: discord.Member, pos: int) -> Optional[str]:
        """Update game state based on position played and return new game status."""
        if pos in self.empty_spots:
            self.empty_spots.remove(pos)
        else:
            return

        if player != self.next_turn[1]:
            return

        print("here")
        self.last_move_timestamp = datetime.datetime.now()

        self.board[(pos - 1) // 3][(pos - 1) % 3] = self.next_turn[0]

        await self.embed_message.edit(
            content=f"It's your turn now, {self.next_turn[1].mention}!",
            embed=self.get_board_embed(),
        )
        self.next_turn = self.next_turn_toggler()

        return self._get_game_status()


class TicTacToe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games_in_progress = {}

        self._check_time_out.start()

    @commands.command(name="ttt")
    async def start_new_game(
        self, ctx: commands.Context, member: discord.Member = None
    ):
        """Start a new tictactoe game between command invoker and mentioned member."""
        # if member == ctx.author:
        #     raise commands.UserInputError('You can\'t play with yourself.')

        new_game = Game(cross_player=ctx.author, naught_player=member)

        new_game.embed_message = await ctx.send(
            content=f"It's your turn now, {new_game.next_turn[1].mention}!",
            embed=new_game.get_board_embed(),
        )

        for emoji in NUMBER_EMOJIS.values():
            await new_game.embed_message.add_reaction(emoji)

        self.games_in_progress[new_game.embed_message] = new_game

    @commands.Cog.listener()
    async def on_reaction_add(
        self, reaction: discord.Reaction, player: discord.Member
    ) -> None:
        """Update games when new reactions are added."""
        if player == self.bot.user:
            return

        if reaction.message not in self.games_in_progress:
            return

        game = self.games_in_progress[reaction.message]

        try:
            await reaction.remove(player)
        except discord.Forbidden:
            pass

        try:
            pos = int(str(reaction.emoji)[0])
        except ValueError:
            return

        await reaction.remove(self.bot.user)

        status = await game.update(player, pos)

        if status is None:
            return

        if status == "in progress":
            return
        elif status == "X":
            await game.embed_message.channel.send(
                f"{game.players['X'].mention} has won the game!"
            )
        elif status == "O":
            await game.embed_message.channel.send(
                f"{game.players['X'].mention} has won the game!"
            )
        else:
            await game.embed_message.channel.send("Game ended in a draw!")

        del self.games_in_progress[game.embed_message]

        try:
            await game.embed_message.clear_reactions()
        except discord.Forbidden:
            pass

    @tasks.loop(seconds=1)
    async def _check_time_out(self) -> None:
        """Check for timeouts in all games."""
        for game in self.games_in_progress.values():
            lapsed = datetime.datetime.now() - game.last_move_timestamp
            if lapsed.seconds > MOVE_TIME_LIMIT:
                await game.embed_message.channel.send(
                    f"{game.next_turn[1].mention} your time is up! Ending game now."
                )
                del self.games_in_progress[game.embed_message]
                try:
                    await game.embed_message.clear_reactions()
                except discord.Forbidden:
                    pass

            elif lapsed.seconds == MOVE_TIME_LIMIT - 5:
                await game.embed_message.channel.send(
                    f"Hurry up {game.next_turn[1].mention}! You have 5 seconds remaining."
                )


def setup(bot: commands.Bot) -> None:
    """Add TicTacToe Cog"""
    bot.add_cog(TicTacToe(bot))
