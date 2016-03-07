#!/usr/bin/env python
# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled

"""
    Telegram bot that sends a voice message with a Dota 2 response.
    Author: Luiz Francisco Rodrigues da Silva <luizfrdasilva@gmail.com>
"""

import json
import logging
import os
import requests

from telegram import Updater
from telegram.dispatcher import run_async
from telegram.utils.botan import Botan

import dota_responses

RESPONSE_DICT = {}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

LOGGER = logging.getLogger(__name__)

# Load config file
with open('config.json') as config_file:
    CONFIGURATION = json.load(config_file)

# Create a Botan tracker object
botan = Botan(CONFIGURATION["botan_token"]) # pylint:disable=invalid-name

def start_command(bot, update):
    """ Handle the /start command. """
    bot.sendMessage(update.message.chat_id, text='Hi, my name is @dotaresponsesbot, I can send'
                                                 ' you voice messages with dota 2 responses, use'
                                                 ' the command /help to see how to use me.')

def help_command(bot, update):
    """ Handle the /help command. """
    bot.sendMessage(update.message.chat_id,
                    text='Usage: /response first blood or /r first blood\n'
                         'If you want to find a sentence for a specific hero, use the flag -h.\n'
                         'Example: /response -htide first blood\n'
                         'Note that there\'s no need to use the full name of the hero. Heros with'
                         ' two or more names should b separated with spaces.\n'
                         'Ex: -hphantom_assassin.')

@run_async
def response_command(bot, update, **kwargs):
    """
        Handle the /response command

        The user sends a message with a desired dota 2 response and the bot responds sends a voice
        message with the best response.
    """
    if len(kwargs["args"]) == 0:
        bot.sendMessage(update.message.chat_id,
                        reply_to_message_id=update.message.message_id,
                        text="Please send a text to get a response.\nSee /help")
        return

    specific_hero = None

    # Remove /response or /r from message
    message = update.message.text.split(" ", 1)[1]

    for arg in kwargs["args"]:
        if arg.find("-h") >= 0:
            specific_hero = arg.replace("-h", "").strip()
            message = message.replace(arg, "")

    query = message
    hero, response = dota_responses.find_best_response(query, RESPONSE_DICT, specific_hero)

    if hero == "" or response is None:
        bot.sendMessage(update.message.chat_id,
                        reply_to_message_id=update.message.message_id,
                        text="Failed to find a response!")
        return

    filename = "resp_{}{}.mp3".format(update.message.chat_id, update.message.message_id)
    with open(filename, "wb") as response_file:
        response_file.write(requests.get(response["url"]).content)

    bot.sendVoice(update.message.chat_id, voice=open(filename, 'rb'))
    os.remove(filename)

def error_handler(bot, update, error): # pylint: disable=unused-argument
    """ Handle polling errors. """
    LOGGER.warn('Update "%s" caused error "%s"', str(update), str(error)) # pylint: disable=deprecated-method

def track(bot, update): # pylint: disable=unused-argument
    """ Print to console and log activity with Botan.io """
    botan.track(update.message,
                update.message.text.split(" ")[0])

    LOGGER.info("New message\nFrom: %s\nchat_id: %s\nText: %s",
                update.message.from_user,
                str(update.message.chat_id),
                update.message.text)


def main():
    """ Main """
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(CONFIGURATION["telegram_token"])

    global RESPONSE_DICT # pylint: disable=global-statement
    # Load the responses
    RESPONSE_DICT = dota_responses.load_response_json(CONFIGURATION["responses_file"])

    # Get the dispatcher to register handlers
    dp = updater.dispatcher # pylint: disable=invalid-name

    # on different commands - answer in Telegram
    dp.addTelegramCommandHandler("start", start_command)
    dp.addTelegramCommandHandler("response", response_command)
    dp.addTelegramCommandHandler("r", response_command)
    dp.addTelegramCommandHandler("response", track)
    dp.addTelegramCommandHandler("r", track)
    dp.addTelegramCommandHandler("help", help_command)

    # log all errors
    dp.addErrorHandler(error_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
