import getopt, sys
import logging
from bot.bot import Bot

handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)-8s [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)

discord_logger = logging.getLogger("discord")
discord_logger.setLevel(logging.INFO)
discord_logger.addHandler(handler)

args = sys.argv[1:]
options = "t:"
long_options = ["token="]

try:
    arguments, values = getopt.getopt(args, options, long_options)
    for current_argument, current_value in arguments:
        if current_argument in ("-t", "--token"):
            token = current_value
    bot = Bot(handler)
    bot.run(token)
except getopt.error as err:
    print(str(err))
    sys.exit(2)
