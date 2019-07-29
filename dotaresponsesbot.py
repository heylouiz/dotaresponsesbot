"""
    Telegram bot that sends a voice message with a Dota 2 response.
    Author: Luiz Francisco Rodrigues da Silva <luizfrdasilva@gmail.com>
"""

import json
import re
import logging
import os
from uuid import uuid4

from telegram import InlineQueryResultVoice
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater, CommandHandler, InlineQueryHandler


# ----- Global Variables ----- #

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
LOGGER = logging.getLogger(__name__)


START_MESSAGE = (
    "Hi, my name is @dotaresponsesbot, I can send Dota 2 voice messages.\n"
    "Type /help to see how to use me."
)

HELP_MESSAGE = (
    "This bot sends Dota 2 voice messages\n"
    "You can use it in any chat, just type "
    "@dotaresponsesbot sentence.\n"
    "Example: @dotaresponsesbot first blood\n"
    "You can also search responses from a specific hero, Example: "
    "@dotaresponsesbot Axe/first blood."
)


responses = []


def load_responses(filename):
    """Load a previous created dict from a file"""
    global responses
    try:
        with open(filename, "r") as response_json:
            responses = json.load(response_json)
    except IOError:
        print("Cannot open {}".format(filename))
        raise


def find_all_responses(query, specific_hero=None):
    for response in responses:
        if "text" not in response:
            continue
        if specific_hero and not re.search(
            specific_hero, response["name"], re.IGNORECASE
        ):
            continue
        if re.search(query, response["text"], re.IGNORECASE):
            yield response


def start_command(bot, update):
    """ Handle the /start command. """
    bot.send_message(update.message.chat_id, text=START_MESSAGE)


def help_command(bot, update):
    """ Handle the /help command. """
    bot.send_message(update.message.chat_id, text=HELP_MESSAGE)


@run_async
def inlinequery(bot, update):
    """Handle the inline requests"""
    query = update.inline_query.query
    inline_results = list()
    hero = None
    response = "first blood"

    if query != "":
        if query.find("/") >= 0:
            hero, response = query.split("/")
        else:
            response = query

    for response in find_all_responses(response.strip(), specific_hero=hero):
        inline_results.append(
            InlineQueryResultVoice(
                id=uuid4(),
                title="{} - {}".format(response["name"], response["text"]),
                voice_url=response["sound_url"],
            )
        )

    bot.answerInlineQuery(update.inline_query.id, results=inline_results[:50])


def error_handler(update, error):
    """ Handle polling errors. """
    LOGGER.warning('Update "%s" caused error "%s"', str(update), str(error))


def main():
    """ Main """
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(os.environ["TELEGRAM_TOKEN"])

    # Load the responses
    load_responses(os.environ["RESPONSES_FILE"])

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler("start", start_command))
    updater.dispatcher.add_handler(CommandHandler("help", help_command))

    # Inline handler
    updater.dispatcher.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    updater.dispatcher.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
