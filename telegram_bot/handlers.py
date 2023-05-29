import json
import os
from os import getenv
from dotenv import load_dotenv
import requests
from .meteo import WeatherService, WeatherServiceException
from .database import Contact, session

load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
tg_base_url = os.getenv('TG_BASE_URL')


class User:
    def __init__(self, first_name, id, is_bot, language_code, last_name, username):
        self.first_name = first_name
        self.id = id
        self.is_bot = is_bot
        self.language_code = language_code
        self.last_name = last_name
        self.username = username


class TelegramHandler:
    user = None

    def send_markup_message(self, text, markup):
        data = {
            'chat_id': self.user.id,
            'text': text,
            'reply_markup': markup
        }
        requests.post(f'{tg_base_url}{bot_token}/sendMessage', json=data)

    def send_message(self, text):
        data = {
            'chat_id': self.user.id,
            'text': text
        }
        requests.post(f'{tg_base_url}{bot_token}/sendMessage', json=data)


class MessageHandler(TelegramHandler):
    def __init__(self, data):
        self.user = User(
            first_name=data.get('from').get('first_name'),
            id=data.get('from').get('id'),
            is_bot=data.get('from').get('is_bot'),
            language_code=data.get('from').get('language_code'),
            last_name=data.get('from').get('last_name'),
            username=data.get('from').get('username')
        )
        self.text = data.get('text')

    def handle(self):
        command, *args = self.text.split()

        if command == '/commands' or command == '/команди':
            commands = [
                {'command': '/weather', 'description': 'Отримати поточну погоду'},
                {'command': '/add', 'description': 'Додати новий контакт'},
                {'command': '/view', 'description': 'Переглянути всі контакти'},
                {'command': '/delete', 'description': 'Видалити контакт за id'},
                {'command': '/stories', 'description': 'Перейти до розповідей'},
                {'command': '/social', 'description': 'Посилання на соціальні мережі'},
                {'command': '/youtube', 'description': 'Посилання на ютуб канал'}
            ]

            message_text = 'Доступні команди:\n\n'
            for cmd in commands:
                message_text += f'{cmd["command"]}: {cmd["description"]}\n'

            self.send_message(message_text)

        elif command == '/add' or command == '/додати':
            handler = PhonebookHandler(self.user, self.text)
            handler.handle()

        elif command == '/view' or command == '/переглянути':
            handler = PhonebookHandler(self.user, self.text)
            handler.handle()

        elif command == '/delete' or command == '/видалити':
            handler = PhonebookHandler(self.user, self.text)
            handler.handle()

        elif command == '/weather':
            if len(args) != 1:
                self.send_message('Невірний формат, викристайте формат: /weather <city>')
            else:
                city = args[0]
                try:
                    geo_data = WeatherService.get_geo_data(city)
                except WeatherServiceException as wse:
                    self.send_message(str(wse))
                else:
                    buttons = []
                    for item in geo_data:
                        test_button = {
                            'text': f'{item.get("name")} - {item.get("country_code")}',
                            'callback_data': json.dumps(
                                {'lat': item.get('latitude'), 'lon': item.get('longitude')}
                            )
                        }
                        buttons.append([test_button])
                    markup = {
                        'inline_keyboard': buttons
                    }
                    self.send_markup_message('Виберіть бажане місто з списку:', markup)

        elif command == '/stories' or command == '/розповіді':
            drive_url = 'https://drive.google.com/drive/folders/1r6h5Ehe_PYWRvJIt8tmShsDjq4DxZYm3'
            buttons = [
                [InlineKeyboardButton("Розповіді", url=drive_url)],
            ]
            reply_markup = InlineKeyboardMarkup(buttons)

            self.send_markup_message('Ось тут розповіді', reply_markup.to_dict())

        elif command == '/social' or command == '/мережі':
            twitter_url = 'https://twitter.com/pohanice'
            facebook_url = 'https://www.facebook.com/profile.php?id=100001918165836'
            github_url = 'https://github.com/Ula1ri'

            buttons = [
                [InlineKeyboardButton("Twitter", url=twitter_url)],
                [InlineKeyboardButton("Facebook", url=facebook_url)],
                [InlineKeyboardButton("GitHub", url=github_url)],
            ]
            reply_markup = InlineKeyboardMarkup(buttons)

            self.send_markup_message('Виберіть бажану мережу:', reply_markup.to_dict())

        elif command == '/youtube' or command == '/ютуб':
            youtube_url = 'https://www.youtube.com/channel/UCZ1ApST9cFYG_qEDppe1wPA'
            buttons = [
                [InlineKeyboardButton("Відео розповіді", url=youtube_url)],
            ]
            reply_markup = InlineKeyboardMarkup(buttons)

            self.send_markup_message('Мої відео', reply_markup.to_dict())

        else:
            self.send_message('Невірна команда. Введіть /commands або /команди щоб побачити всі доступні команди.')


class CallbackHandler(TelegramHandler):

    def __init__(self, data):
        self.user = User(
            first_name=data.get('from').get('first_name'),
            id=data.get('from').get('id'),
            is_bot=data.get('from').get('is_bot'),
            language_code=data.get('from').get('language_code'),
            last_name=data.get('from').get('last_name'),
            username=data.get('from').get('username')
        )
        self.callback_data = json.loads(data.get('data'))

    def handle(self):
        try:
            weather = WeatherService.get_current_weather(**self.callback_data)
        except WeatherServiceException as wse:
            self.send_message(str(wse))
        else:
            message = f"Temperature: {weather['temperature']}°C\n"
            message += f"Windspeed: {weather['windspeed']} km/h\n"
            message += f"Wind direction: {weather['winddirection']}°\n"
            message += f"Weather code: {weather['weathercode']}\n"
            message += "It's day time" if weather['is_day'] else "It's night time"
            self.send_message(message)


class PhonebookHandler(TelegramHandler):
    def __init__(self, user, text):
        super().__init__()
        self.user = user
        self.text = text

    def handle(self):
        command, *args = self.text.split()

        if command == '/add' or command == '/додати':
            if len(args) < 3:
                self.send_message('Недійсна команда. Використайте формат: /додати або /add <first_name> <last_name> <phone_number>')
            else:
                first_name, last_name, phone_number = args
                contact = Contact(first_name=first_name, last_name=last_name, phone=phone_number,
                                  telegram_id=self.user.id)
                session.add(contact)
                session.commit()
                self.send_message('Контакт успішно доданий.')

        elif command == '/view' or command == '/переглянути':
            contacts = session.query(Contact).filter_by(telegram_id=self.user.id).all()

            if contacts:
                for contact in contacts:
                    message_text = f'{contact.id} {contact.first_name} {contact.last_name} - \n{contact.phone}'
                    self.send_message(message_text)
            else:
                self.send_message('Ваша телефонна книга пуста.')

        elif command == '/delete' or command == '/видалити':
            if len(args) != 1:
                self.send_message('Недійсна команда. Використайтe формат: /видалити або /delete <contact_id>')
            else:
                contact_id = args[0]
                contact = session.query(Contact).filter_by(id=contact_id, telegram_id=self.user.id).first()

                if contact_id and contact:
                    session.delete(contact)
                    session.commit()
                    self.send_message('Ваш контакт успішно видалено.')
                else:
                    self.send_message('Контакт з таким id не знайдено.')

        else:
            pass
