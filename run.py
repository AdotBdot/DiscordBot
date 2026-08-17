import getopt, sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from bot.bot import Bot

# Setting up logging

Path("logs").mkdir(parents=True, exist_ok=True)

console_handler = logging.StreamHandler()
file_handler = logging.FileHandler("logs/latest.txt", mode="w", encoding="utf-8")

formatter = logging.Formatter("%(asctime)s %(levelname)-8s [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S")

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

discord_logger = logging.getLogger("discord")
discord_logger.setLevel(logging.INFO)
discord_logger.addHandler(console_handler)
discord_logger.addHandler(file_handler)
discord_logger.propagate = False

# Starting bot

args = sys.argv[1:]
options = "t:"
long_options = ["token="]

try:
    token = ""
    arguments, values = getopt.getopt(args, options, long_options)
    for current_argument, current_value in arguments:
        if current_argument in ("-t", "--token"):
            token = current_value

    if token == "" or token is None:
        print("Token is required. Use -t or --token to provide the token.")
        exit(0)
    else:
        bot = Bot(console_handler, file_handler)
        bot.run(token)
except getopt.error as err:
    print(str(err))
    sys.exit(2)
