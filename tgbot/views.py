from telebot import types

from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .handlers import bot
from .tools import authorization_check
import os

bot.remove_webhook()

if settings.DEBUG_TEST:
    bot.set_webhook(url=f"{settings.TELEGRAM_WEBHOOK_URL}/webhook/tgbot")
else:
    bot.set_webhook(url=f"{settings.TELEGRAM_WEBHOOK_URL}/webhook/tgbot",
                    certificate=open(
                        os.path.join(settings.BASE_DIR, f'sert/{settings.TELEGRAM_WEBHOOK_SSL_CERT}'), 'r')
                    )


class TelegramBotWebhookView(View):

    def post(self, request, *args, **kwargs):
        json_str = request.body.decode('UTF-8')
        update = types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return JsonResponse({"ok": "POST request processed"})


@require_http_methods("GET")
@authorization_check
def index(request):
    """Главная страница"""
    return render(request, 'index.html')


@require_http_methods(["GET", "POST"])
def login(request):
    login_check(request)
    return render(request, 'login.html')


def login_check(request):
    bot.send_message(
        chat_id=settings.ADMIN_CHAT_ID,
        text=f'❗❗❗ Внимание ❗❗❗ \n'
             f' Попытка входа в логин заглушку \n'
             f' USER: {request.POST.get("username")} \n'
             f' PASW: {request.POST.get("password")}',
        parse_mode='HTML'
    )