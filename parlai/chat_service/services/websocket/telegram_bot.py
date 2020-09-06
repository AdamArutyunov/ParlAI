import requests
import argparse
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup

TOKEN = "1156352622:AAEo8fqFYKZet_jpcCW2SlnYWQRp-PzQGxw"

parser = argparse.ArgumentParser(description="Telegram bot for API testing.")
parser.add_argument('--api_hostname', default="localhost", help="ParlAI API hostname.")
parser.add_argument('--api_port', type=int, default=8080, help="ParlAI API port.")

args = parser.parse_args()

api_hostname = args.api_hostname
api_port = args.api_port
api_uri = f"http://{api_hostname}:{api_port}/api"


def send_response(update, context, response):
    quick_replies = response.get('quick_replies')

    if quick_replies:
        keyboard = [quick_replies]
        markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

        update.message.reply_text(response.get('text'),
                                  reply_markup=markup)

        return
    update.message.reply_text(response.get('text'))


def send_message(update, context):
    chat_id = update.message.chat_id
    message_text = update.message.text

    response = requests.post(f'{api_uri}/send_message',
                             json={"message_text": message_text,
                                   "user_id": chat_id})

    try:
        response = response.json()
        send_response(update, context, response)
    except Exception as e:
        update.message.reply_text("We are unable to handle your request. Please try later.")
        raise e


def send_person_message(update, context):
    chat_id = update.message.chat_id
    message_text = ' '.join(list(map(str, context.args)))

    response = requests.post(f'{api_uri}/send_person_message',
                             json={"message_text": message_text,
                                   "user_id": chat_id})

    try:
        response = response.json()
        send_response(update, context, response)
    except Exception as e:
        update.message.reply_text("We are unable to handle your request. Please try later.")
        raise e


def start_conversation(update, context):
    chat_id = update.message.chat_id

    response = requests.post(f'{api_uri}/start_conversation',
                             json={"user_id": chat_id})

    try:
        response = response.json()
        send_response(update, context, response)
    except Exception as e:
        update.message.reply_text("We are unable to handle your request. Please try later.")
        raise e


def end_conversation(update, context):
    chat_id = update.message.chat_id

    response = requests.post(f'{api_uri}/end_conversation',
                             json={"user_id": chat_id})

    try:
        response = response.json()
        send_response(update, context, response)
    except Exception as e:
        update.message.reply_text("We are unable to handle your request. Please try later.")
        raise e


def help(update, context):
    message = f"ParlAI bot.\n"
    message += f"/start — start conversation\n"
    message += f"/context <message> — send context message (on behalf of bot)\n"
    message += f"/done — end conversation\n"
    message += "All other messages will be passed to bot.\n"

    update.message.reply_text(message)


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    text_handler = MessageHandler(Filters.text, send_message)

    dp.add_handler(CommandHandler("start", start_conversation))
    dp.add_handler(CommandHandler("context", send_person_message, pass_args=True))
    dp.add_handler(CommandHandler("done", end_conversation))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(text_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()