"""handlers.py - Перехватчик сообщений и команд от пользователей ТГ бота
"""
import os
import logging
from django.utils.timezone import now
# import telebot
from telebot import TeleBot
from .tools import send_email, check_is_registrations

from django.conf import settings

from .models import User, Profile, ProfileSearch, ProfileLikes
from .markup import *
from .bot import Bot
from .registration import Registration
from .search import Search


bot = TeleBot(settings.TELEGRAM_TOKEN)
registration = Registration(bot)
search = Search(bot)

bot.register_message_handler(registration.start_message, commands=['start'])
bot.register_callback_query_handler(registration.callback_change_profile,
                                    func=lambda call: call.data.startswith('profile_'))
bot.register_callback_query_handler(search.action,
                                    func=lambda call: call.data.startswith('action_'))
bot.register_callback_query_handler(search.callback_change_profile_search,
                                    func=lambda call: call.data.startswith('search_'))
# можно поменять
bot.register_message_handler(registration.show_user_profile, commands=['profile'])
bot.register_message_handler(registration.send_bug_message, commands=['bug'])
bot.register_message_handler(search.bot_message, content_types=['text'])
