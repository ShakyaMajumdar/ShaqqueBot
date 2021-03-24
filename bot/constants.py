import os
import pathlib
from typing import NamedTuple

import yaml

# env vars
PREFIX = os.getenv("PREFIX") or "!"
TOKEN = os.getenv("TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_LIVESCORE6_HOST = os.getenv("RAPIDAPI_LIVESCORE6_HOST")


BOT_REPO_URL = "https://github.com/ShakyaMajumdar/ShaqqueBot"

# paths
EXTENSIONS = pathlib.Path("bot/exts/")
LOG_FILE = pathlib.Path("log/shaqquebot.log")


class Emojis(NamedTuple):
    cross = "<:x:818886273871118398>"
    naught = "<:o:818886375268810753>"


class Channels(NamedTuple):
    general = 788379519849201696


class Roles(NamedTuple):
    pass


# Bot replies
with pathlib.Path("bot/resources/bot_replies.yml").open(encoding="utf8") as file:
    bot_replies = yaml.safe_load(file)
    ERROR_REPLIES = bot_replies["ERROR_REPLIES"]
    POSITIVE_REPLIES = bot_replies["POSITIVE_REPLIES"]
    NEGATIVE_REPLIES = bot_replies["NEGATIVE_REPLIES"]
