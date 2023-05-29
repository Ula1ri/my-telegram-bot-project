import os
from os import getenv
from dotenv import load_dotenv
import requests
from telegram_bot import app
from flask import request
from pprint import pprint
from .handlers import MessageHandler, CallbackHandler, PhonebookHandler, User


load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
tg_base_url = os.getenv('TG_BASE_URL')


@app.route('/', methods=["POST"])
def hello():
    handler = None

    if message := request.json.get('message'):
        handler = MessageHandler(message)
    elif callback := request.json.get('callback_query'):
        handler = CallbackHandler(callback)

    if handler is not None:
        handler.handle()

    return 'ok!', 200
