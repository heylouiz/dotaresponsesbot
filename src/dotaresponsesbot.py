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
from uuid import uuid4

from telegram import InlineQueryResultVoice
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater, CommandHandler, RegexHandler, InlineQueryHandler
from telegram.utils.botan import Botan

import dota_responses

RESPONSE_DICT = {}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

LOGGER = logging.getLogger(__name__)

def start_command(bot, update):
    """ Handle the /start command. """
    bot.send_message(update.message.chat_id, text='Hi, my name is @dotaresponsesbot, I can send'
                                                 ' you voice messages with dota 2 responses, use'
                                                 ' the command /help to see how to use me.')

def help_command(bot, update):
    """ Handle the /help command. """
    bot.send_message(update.message.chat_id,
                    text='Usage: /response first blood or /r first blood\n'
                         'If you want to find a sentence for a specific hero, use the flag -h.\n'
                         'Example: /response -htide first blood\n'
                         'Note that there\'s no need to use the full name of the hero. Heros with'
                         ' two or more names should b separated with spaces.\n'
                         'Ex: -hphantom_assassin.')

@run_async
def response_command(bot, update, args, responses_dict):
    """
        Handle the /response command

        The user sends a message with a desired dota 2 response and the bot responds sends a voice
        message with the best response.
    """
    if len(args) == 0:
        bot.send_message(update.message.chat_id,
                        reply_to_message_id=update.message.message_id,
                        text="Please send a text to get a response.\nSee /help")
        return

    specific_hero = None

    # Remove /response or /r from message
    message = update.message.text.split(" ", 1)[1]

    for arg in args:
        if arg.find("-h") >= 0:
            specific_hero = arg.replace("-h", "").strip()
            message = message.replace(arg, "")

    query = message
    hero, response = dota_responses.find_best_response(query, responses_dict, specific_hero)

    if hero == "" or response is None:
        bot.send_message(update.message.chat_id,
                        reply_to_message_id=update.message.message_id,
                        text="Failed to find a response!")
        return

    filename = "resp_{}{}.mp3".format(update.message.chat_id, update.message.message_id)
    with open(filename, "wb") as response_file:
        response_file.write(requests.get(response["url"]).content)

    bot.send_voice(update.message.chat_id, voice=open(filename, 'rb'))
    os.remove(filename)

@run_async
def inlinequery(bot, update, response_dict):
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

    results = dota_responses.find_all_responses(response.strip(), response_dict, specific_hero=hero)

    for hero, responses in results.items():
        for response in responses:
            inline_results.append(InlineQueryResultVoice(id=uuid4(),
                                                         title="{} - {}".format(hero,
                                                                                response["text"]),
                                                         voice_url=response["url"]))

    bot.answerInlineQuery(update.inline_query.id, results=inline_results[:50])


def error_handler(update, error):
    """ Handle polling errors. """
    LOGGER.warning('Update "%s" caused error "%s"', str(update), str(error))

def track(update, botan):
    """ Print to console and log activity with Botan.io """
    botan.track(update.message,
                update.message.text.split(" ")[0])

    LOGGER.info("New message\nFrom: %s\nchat_id: %s\nText: %s",
                update.message.from_user,
                str(update.message.chat_id),
                update.message.text)


def main():
    """ Main """

    # Load config file
    with open('config.json') as config_file:
        CONFIGURATION = json.load(config_file)

    # Create a Botan tracker object
    botan = Botan(CONFIGURATION["botan_token"])

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(CONFIGURATION["telegram_token"])

    # Load the responses
    response_dict = dota_responses.load_response_json(CONFIGURATION["responses_file"])

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler("start", start_command))
    updater.dispatcher.add_handler(CommandHandler("help", help_command))

    response_cmd_lambda = lambda bot, update, args: response_command(bot,
                                                                     update,
                                                                     args,
                                                                     response_dict)

    # Inline handler
    updater.dispatcher.add_handler(InlineQueryHandler(lambda bot, update:
                                                        inlinequery(bot,
                                                                    update,
                                                                    response_dict)))

    # Command handlers
    updater.dispatcher.add_handler(CommandHandler("response", response_cmd_lambda, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler("r", response_cmd_lambda, pass_args=True))

    # Track handlers
    updater.dispatcher.add_handler(CommandHandler("response",
                                                  lambda bot, update: track(update, botan)),
                                                  group=1)
    updater.dispatcher.add_handler(CommandHandler("r",
                                                  lambda bot, update: track(update, botan)),
                                                  group=1)



    # log all errors
    updater.dispatcher.add_error_handler(lambda bot, update: error_handler(update, botan))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
