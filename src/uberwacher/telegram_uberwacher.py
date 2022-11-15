#!/usr/bin/env python3
import os
import logging
from gpiozero import MotionSensor
from functools import wraps

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler

BOT_TOKEN_ENV_VAR = "UBERWACHER_BOT_TOKEN"
DEFAULT_GPIO_PIN = 14
DEFAULT_SUBSCRIBERS_FILE = "./subscribers"


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
    parser.add_argument('--whitelist',
                        dest='whitelist',
                        required=False,
                        type=str,
                        help="Specify a comma-separated list of users allowed to access this bot. "
                             "This argument can also be a filename. "
                             "Everyone's allowed to use it by default.")
    parser.add_argument('--subscribers',
                        dest='subscribers',
                        required=False,
                        default=DEFAULT_SUBSCRIBERS_FILE,
                        type=str,
                        help="Specify a file with chat identifiers stored. "
                             f"Default is {DEFAULT_SUBSCRIBERS_FILE}")
    options = parser.parse_args()
    return options


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt="%m/%d/%Y %I:%M:%S %p %Z",
                    level=logging.INFO,
                    # filename="main.log"
                    )
logger = logging.getLogger('telegram-uberwacher')

INFO_MESSAGES = {'start': "ALARMS ACTIVATED. The bot will spam you with messages "
                          "if it sees movements around and you don't turn it off.",
                 'help': "Use this bot via the /start command. "
                         "Press a button to turn it off when it sees a movement if that's you."}

global gpio_pin
global WHITELIST
global SUBSCRIBERS
global SUBSCRIBERS_FILE


def whitelist_only(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user = update.effective_user
        if WHITELIST and user.username not in WHITELIST:
            logger.warning(f"Unauthorized access denied for {user.username}.")
            text = (
                "🚫 *ACCESS DENIED*\n"
                "Sorry, you are *not authorized* to use this command"
            )
            update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            return
        return func(update, context, *args, **kwargs)

    return wrapped


class SubscriberNotifier:
    def __init__(self, bot):
        self.bot = bot

    def start(self, chat_id: int):
        global gpio_pin
        sensor = MotionSensor(gpio_pin)

        bot = self.bot

        def on_motion():
            logger.info("MOTION DETECTED")
            bot.send_message(chat_id,
                             "MOTION DETECTED",
                             parse_mode=ParseMode.MARKDOWN
                             )

        def no_motion():
            logger.info("[*] No motion detected")

        sensor.wait_for_no_motion()

        sensor.when_motion = on_motion
        sensor.when_no_motion = no_motion
        bot.send_message(chat_id,
                              INFO_MESSAGES['start'],
                              parse_mode=ParseMode.MARKDOWN)
        logger.info(f"A new motion sensor configured for chat id {chat_id}")
        while True:
            pass


class MotionSensorNotifier:
    def __init__(self):
        pass

    def start(self, update):
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
        while True:
            pass


# 1282513876
@whitelist_only
def start(update, context):
    """Send a message when the command /start is issued."""
    chat_id = update.message.chat.id

    global SUBSCRIBERS
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, 'r') as f:
            SUBSCRIBERS = [int(line.strip()) for line in f.readlines() if line.strip()]

    if chat_id in SUBSCRIBERS:
        logger.info(f"A chat with ID {chat_id} is already stored in the subscribers list")
        update.message.reply_text("You've already subscribed for notifications",
                                  parse_mode=ParseMode.MARKDOWN)
    else:
        motion_sensor_notifier = MotionSensorNotifier()
        motion_sensor_notifier.start(update)

        with open(SUBSCRIBERS_FILE, 'a') as f:
            f.write(f"{chat_id}")
            f.write(os.linesep)

@whitelist_only
def show_help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(INFO_MESSAGES['help'],
                              parse_mode=ParseMode.MARKDOWN)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f"Update {update} caused error {context.error}")


class UberwacherBot:
    def __init__(self, bot_token: str, gpio_pin_num: int, whitelist: [], subscribers: []):
        self.bot_token = bot_token
        self.gpio_pin = gpio_pin_num
        self.whitelist = whitelist
        self.subscribers = subscribers

        global gpio_pin
        gpio_pin = self.gpio_pin
        global WHITELIST
        WHITELIST = self.whitelist
        global SUBSCRIBERS
        SUBSCRIBERS = self.subscribers

    def start(self):
        updater = Updater(self.bot_token, use_context=True)

        dp = updater.dispatcher

        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", show_help))
        dp.add_error_handler(error)

        updater.start_polling()

        if self.subscribers:
            for sub in self.subscribers:
                sub_notifier = SubscriberNotifier(bot=updater.bot)
                sub_notifier.start(chat_id=sub)

        logger.info("BOT DEPLOYED. Ctrl+C to terminate")

        updater.idle()


def main():
    options = get_arguments()

    if options.whitelist:
        if os.path.exists(options.whitelist):
            with open(options.whitelist, "r") as f:
                whitelist = [line.strip() for line in f.readlines() if line.strip()]
        else:
            whitelist = options.whitelist.split(",")
    else:
        whitelist = []

    global SUBSCRIBERS_FILE
    SUBSCRIBERS_FILE = options.subscribers
    if os.path.exists(options.subscribers):
        with open(options.subscribers, "r") as f:
            subscribers = [line.strip() for line in f.readlines() if line.strip()]
    else:
        subscribers = []

    uberwacher_bot = UberwacherBot(bot_token=options.token,
                                   gpio_pin_num=options.gpio_pin,
                                   whitelist=whitelist,
                                   subscribers=subscribers)
    uberwacher_bot.start()


if __name__ == '__main__':
    main()
