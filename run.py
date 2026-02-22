import getopt, sys
from bot.bot import Bot

args = sys.argv[1:]
options = "t:"
long_options = ["token="]

try:
    arguments, values = getopt.getopt(args, options, long_options)
    for current_argument, current_value in arguments:
        if current_argument in ("-t", "--token"):
            token = current_value
    bot = Bot()
    bot.run(token)
except getopt.error as err:
    print(str(err))
    sys.exit(2)


