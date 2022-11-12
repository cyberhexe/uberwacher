#!/usr/bin/env python3
import os
import logging
from gpiozero import MotionSensor, LED

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler

BOT_TOKEN_ENV_VAR = "UBERWACHER_BOT_TOKEN"
DEFAULT_GPIO_PIN = 14




def get_arguments():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Telegram Uberwacher Bot')
    parser.add_argument('-t',
                        "--token",
                        dest="token",
                        required=False,
                        default=os.getenv(BOT_TOKEN_ENV_VAR),
                        type=str,
                        help=f"The bot's token. \
                        If omitted, the script takes the value stored in the {BOT_TOKEN_ENV_VAR} environment variable.")
    parser.add_argument('--gpio-pin',
                        dest='gpio_pin',
                        required=False,
                        default=DEFAULT_GPIO_PIN,
                        type=int,
                        help="Specify the GPIO pin to read the motion sensor's data from. "
                             f"Default is {DEFAULT_GPIO_PIN}.")
    options = parser.parse_args()
    return options


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    # filename="main.log"
                    )
logger = logging.getLogger('telegram-uberwacher')

INFO_MESSAGES = {'start': "ALARMS ACTIVATED. The bot will spam you with messages "
                          "if it sees movements around and you don't turn it off.",
                 'help': "Use this bot via the /start command. "
                         "Press a button to turn it off when it sees a movement if that's you."}

global gpio_pin

global sensor

def start(update, context):
    """Send a message when the command /start is issued."""
    global sensor
    sensor = ''
    if sensor:
        update.message.reply_text("ALARMS ALREADY ACTIVATED. Consider restarting the bot if that seems wrong.")

    global gpio_pin
    sensor = MotionSensor(gpio_pin)

    def on_motion():
        update.message.reply_text("MOTION DETECTED",
                                  parse_mode=ParseMode.MARKDOWN)

    def no_motion():
        logging.info("[*] No motion detected")

    update.message.reply_text("Do not move, setting up the PIR sensor...",
                              parse_mode=ParseMode.MARKDOWN)

    sensor.wait_for_no_motion()

    sensor.when_motion = on_motion
    sensor.when_no_motion = no_motion
    update.message.reply_text(INFO_MESSAGES['start'],
                              parse_mode=ParseMode.MARKDOWN)


def show_help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(INFO_MESSAGES['help'],
                              parse_mode=ParseMode.MARKDOWN)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f"Update {update} caused error {context.error}")


class UberwacherBot:
    def __init__(self, bot_token: str, gpio_pin_num: int):
        self.bot_token = bot_token
        self.gpio_pin = gpio_pin_num

        global gpio_pin
        gpio_pin = self.gpio_pin

    def start(self):
        updater = Updater(self.bot_token, use_context=True)

        dp = updater.dispatcher

        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", show_help))
        dp.add_error_handler(error)

        updater.start_polling()
        logger.info("BOT DEPLOYED. Ctrl+C to terminate")

        updater.idle()


def main():
    options = get_arguments()
    uberwacher_bot = UberwacherBot(bot_token=options.token, gpio_pin_num=options.gpio_pin)
    uberwacher_bot.start()


if __name__ == '__main__':
    main()
