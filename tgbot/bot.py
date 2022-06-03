from .abstract import AbstractBot
from django.conf import settings
from .tools import log, check_is_registrations
from .models import User
import os
import logging
from .markup import gen_markup_for_profile


class Bot(AbstractBot):

    def __init__(self, bot):
        self.bot = bot
        self.class_user = User
        # self._gen_markup_for_profile = gen_markup_for_profile

    @log
    def send_message_to_admin(self, message):
        """Команда по отправке сообщения админу в ТГ
        :param Message message: Текст сообщения"""
        self.bot.send_message(
            chat_id=settings.ADMIN_CHAT_ID,
            text=message,
            parse_mode='HTML'
        )
        # send_email(bug)

    @log
    def send_bug_message(self, message):
        """Команда /bug от пользователя
        Пользователь отправляет сообщение о некорректной работе бота.
        Сообщение логируется в консоль и файл
        :param Message message: Сообщение от пользователя
        """
        text = '<b>Отправьте сообщение об ошибке администратору бота</b>\n'
        text += 'Укажите в какой момент времени и какая ошибка возникла'
        message = self.bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode='HTML'
        )
        self.bot.register_next_step_handler(message, self._process_bug_step)

    @log
    def _process_bug_step(self, message):
        """Логирование сообщения об ошибке в боте от пользователя
        :param Message message: Сообщение от пользователя
        """
        bug = message.text
        text = '<b>Спасибо за информацию👍</b>\n'
        text += 'Наша команда проверит информацию и свяжется с вами!'
        self.bot.reply_to(
            message=message,
            text=text,
            parse_mode='HTML'
        )
        bug = f'BUG from {message.chat.id}:\n Cообщение: {bug} \n\n'
        bug += f'<a href="tg://user?id={message.chat.id}">Ссылка</a>  @{message.chat.username}'
        logging.warning(message)
        self.send_message_to_admin(bug)

    @log
    def show_user_profile(self, message):
        """Команда /profile от пользователя
        При получении команды отображается текущий профиль пользователя.
        При отсутствии или незаконченной регистрации соответствующее уведомление.
        :param Message message: Сообщение от пользователя
        """
        user = User.objects.get(chat_id=message.chat.id)
        text = f'<b>👤Имя: </b>{user.profile.name}\n'
        text += f'<b>🔢Возраст: </b>{user.profile.age}\n'
        if user.profile.sex == 'M':
            text += '<b>🚹Пол: </b> Мужчина\n'
        elif user.profile.sex == 'W':
            text += '<b>🚺Пол: </b> Женщина\n'
        elif user.profile.sex == 'O':
            text += '<b>Пол: </b> Другое\n'

        text += f'<b>🖌️Описание: </b>{user.profile.description}\n\n'
        text += '<i>Так выглядит ваш профиль</i>\n'
        text += 'Вы можете изменить следующие параметры:'
        self.bot.send_photo(
            chat_id=user.chat_id,
            photo=self.get_user_avatar(user),
            caption=text,
            reply_markup=gen_markup_for_profile(user),
            parse_mode='HTML'
        )

    # изменить фото по дефолту
    @log
    def get_user_avatar(self, user):
        """Получение изображения профиля текущего пользователя
        :param User user: Текущий пользователь бота
        :return: Аватар пользователя
        :rtype: bytes
        """
        save_path = os.path.join(settings.MEDIA_ROOT, 'images/avatars/')
        file_name = f"{user.chat_id}.jpg"
        try:
            complete_name = os.path.join(save_path, file_name)
            with open(complete_name, "rb") as img:
                avatar = img.read()
                return avatar
        except:
            complete_name = os.path.join(
                settings.STATIC_ROOT, 'tgbot/images/unknown.webp'
            )
            with open(complete_name, "rb") as img:
                avatar = img.read()
                return avatar