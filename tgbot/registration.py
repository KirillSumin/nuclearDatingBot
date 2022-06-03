import os
from .bot import Bot
from .tools import log, log_act
from django.conf import settings
from .models import User, Profile, ProfileSearch, ProfileLikes, ActType, LogUsers
from .markup import *
from django.utils.timezone import now
from .abstract import AbstractRegistration
from .bot import Bot



class Registration(AbstractRegistration, Bot):

    @log
    def start_message(self, message):
        """Команда /start от пользователя
        При получении команды начинается регистрация текущего пользователя.
        При завершенной регистрации команда отправляет приветствие.
        :param Message message: Сообщение от пользователя
        """
        sticker_path = os.path.join(
            settings.STATIC_ROOT, 'tgbot/images/welcome.webp'
        )

        with open(sticker_path, 'rb') as sticker:
            self.bot.send_sticker(message.chat.id, sticker.read())
        print("--------------------------")
        user, created = User.objects.get_or_create(chat_id=message.chat.id)
        log_act(user, 'start')
        if created or not user.profile.is_registered:
            user.first_name = message.chat.first_name
            user.username = message.chat.username
            user.save()

            text = '<b>Приветик☺</b>\n\n'

            Profile.objects.get_or_create(user=user)
            ProfileSearch.objects.get_or_create(user=user)
            ProfileLikes.objects.get_or_create(user=user)

            text += 'Чтобы начать знакомства, необходимо завести анкету.\n'

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(
                text="❤️Регистрация анкеты",
                callback_data="profile_registration"
            ))

            if not user.username:
                _text = 'К сожалению в вашем аккаунте username отсутствует,' \
                        ' если хочешь чтобы с тобой могли связаться то включи' \
                        ' возможность пересылки сообщения' \
                        ' (Конфиденциальность -> Пересылка сообщений -> Всн)'
            self.bot.send_message(
                chat_id=message.chat.id,
                text=_text,
                parse_mode='HTML'
            )

            self.bot.send_message(
                chat_id=message.chat.id,
                text=text,
                reply_markup=markup,
                parse_mode='HTML'
            )
        else:
            text = "Ку-ку🙂\n"
            text += "Твоя анкета уже есть у нас. Переходи к поиску\n"
            self.bot.send_message(
                chat_id=message.chat.id,
                text=text,
                reply_markup=gen_main_markup(),
                parse_mode='HTML'
            )

    @log
    def callback_change_profile(self, call):
        """Изменение параметров текущего профиля пользователя
        Происходит переход к шагу цепочки параметра профиля как при регистрации.
        Дальнейший переход по цепочке не происходит (is_registered = True)
        :param call: Callback от inline-клавиши
        :raise User.DoesNotExist: Доступ в профиль при отсутствии регистрации
        """
        try:
            self.bot.edit_message_reply_markup( # возможная ошибка из-за того, 
                chat_id=call.from_user.id,      # что пройдёт 3 дня и не получится изменить сообщение            
                message_id=call.message.message_id
            )

            user = User.objects.get(chat_id=call.from_user.id)
            user.last_use = now()

            if call.data == 'profile_registration':
                self.bot.send_message(
                    chat_id=call.from_user.id,
                    text="Как вас зовут?"
                )
                self.bot.register_next_step_handler(call.message, self.process_name_step, user)
                self.bot.answer_callback_query(call.id)
                return

            elif call.data == 'profile_edit_name':
                self.bot.send_message(
                    chat_id=call.from_user.id,
                    text="Укажите ваше имя:"
                )
                self.bot.register_next_step_handler(call.message, self.process_name_step, user)
                self.bot.answer_callback_query(call.id)
                return

            elif call.data == 'profile_edit_age':
                self.bot.send_message(
                    chat_id=call.from_user.id,
                    text="Укажите ваш возраст:"
                )
                self.bot.register_next_step_handler(call.message, self.process_age_step, user)
                self.bot.answer_callback_query(call.id)
                return

            elif call.data == 'profile_edit_sex':
                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                                   resize_keyboard=True)
                markup.add('Мужчина', 'Женщина', 'Другое')
                self.bot.send_message(
                    chat_id=call.from_user.id,
                    text="Укажите ваш пол:",
                    reply_markup=markup
                )
                self.bot.register_next_step_handler(call.message, self.process_sex_step, user)
                self.bot.answer_callback_query(call.id)
                return

            elif call.data == 'profile_edit_description':
                self.bot.send_message(
                    chat_id=call.from_user.id,
                    text="Укажите описание:"
                )
                self.bot.register_next_step_handler(call.message,
                                                    self.process_description_step, user)
                self.bot.answer_callback_query(call.id)
                return
            elif call.data == 'profile_edit_avatar':
                self.bot.send_message(
                    chat_id=call.from_user.id,
                    text="Пришлите ваше фото:"
                )
                self.bot.register_next_step_handler(call.message, self.process_photo_step,
                                               user)
                self.bot.answer_callback_query(call.id)
                return

            elif call.data == 'profile_edit_active':
                user.profile.is_active = not user.profile.is_active
                user.profile.save()
                log_act(user, 'is_prof_active', str(user.profile.is_active))
                self.show_user_profile(call.message)
                self.bot.answer_callback_query(call.id, 'Статус анкеты изменен')
                return

        except User.DoesNotExist:
            self.bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=call.message.message_id,
                text="Вы не завели анкету!\nВоспользуйтесь командой:\n/start"
            )

    @log
    def process_name_step(self, message, user):
        """Шаг в цепочке регистрации пользователя (указание имени)
        :param Message message: Сообщение от пользователя
        :param User user: Текущий пользователь
        """
        name = message.text
        if len(name) > 20:
            self.bot.reply_to(
                message=message,
                text='Ваше имя слишком длинное, используйте до 20 сим.'
            )
            self.bot.register_next_step_handler(message, self.process_name_step, user)
            return
        user.profile.name = name
        user.profile.save()
        log_act(user, 'name', name)
        self.bot.send_message(chat_id=message.chat.id, text='Имя установлено!')
        if user.profile.is_registered:
            self.show_user_profile(message)
        else:
            message = self.bot.reply_to(message, 'Сколько вам лет?')
            self.bot.register_next_step_handler(message, self.process_age_step, user)

    @log
    def process_age_step(self, message, user):
        """Шаг в цепочке регистрации пользователя (указание возраста)
        :param Message message: Сообщение от пользователя
        :param User user: Текущий пользователь
        """
        age = message.text
        if not age.isdigit() or not 13 <= int(age) <= 100:
            message = self.bot.reply_to(
                message=message,
                text='Укажите возраст цифрами от 13 до 100'
            )
            self.bot.register_next_step_handler(message, self.process_age_step, user)
            return
        user.profile.age = age
        user.profile.save()
        log_act(user, 'age', age)
        self.bot.send_message(chat_id=message.chat.id, text='Возраст установлен!')
        if user.profile.is_registered:
            self.show_user_profile(message)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                               resize_keyboard=True)
            markup.add('Мужчина', 'Женщина', 'Другое')
            message = self.bot.reply_to(
                message=message,
                text='Укажите ваш пол',
                reply_markup=markup
            )
            self.bot.register_next_step_handler(message, self.process_sex_step, user)

    @log
    def process_sex_step(self, message, user):
        """Шаг в цепочке регистрации пользователя (указание пола)
        :param Message message: Сообщение от пользователя
        :param User user: Текущий пользователь
        """
        sex = message.text
        if sex == 'Мужчина':
            user.profile.sex = 'M'
            user.profilesearch.sex = 'W'
        elif sex == 'Женщина':
            user.profile.sex = 'W'
            user.profilesearch.sex = 'M'
        elif sex == 'Другое':
            user.profile.sex = 'O'
            user.profilesearch.sex = 'O'
        else:
            message = self.bot.reply_to(
                message=message,
                text='Выберите пол из предложенных вариантов'
            )
            self.bot.register_next_step_handler(message, self.process_sex_step, user)
            return
        user.profile.save()
        user.profilesearch.save()
        log_act(user, 'sex', sex)
        if user.profile.is_registered:
            self.bot.send_message(
                chat_id=message.chat.id,
                text='Пол установлен!',
                reply_markup=gen_main_markup()
            )
        else:
            self.bot.send_message(
                chat_id=message.chat.id,
                text='Пол установлен!',
                reply_markup=types.ReplyKeyboardRemove()
            )
            message = self.bot.send_message(
                chat_id=message.chat.id,
                text='Укажите описание о себе до 400 сим.',
                reply_markup=types.ReplyKeyboardRemove()
            )
            self.bot.register_next_step_handler(message, self.process_description_step, user)

    @log
    def process_description_step(self, message, user):
        """Шаг в цепочке регистрации пользователя (указание описания профиля)
        :param Message message: Сообщение от пользователя
        :param User user: Текущий пользователь
        """
        description = message.text
        if len(description) > 400:
            message = self.bot.reply_to(
                message=message,
                text='Слишком длинное описание, до 400 сим.'
            )
            self.bot.register_next_step_handler(message, self.process_description_step,
                                           user)
            return
        user.profile.description = description
        user.profile.save()
        log_act(user, 'description', description)
        self.bot.send_message(
            chat_id=message.chat.id,
            text='Описание установлено!'
        )
        if user.profile.is_registered:
            self.show_user_profile(message)
        else:
            message = self.bot.reply_to(message, 'Пришлите ваше фото')
            self.bot.register_next_step_handler(message, self.process_photo_step, user)

    @log
    def process_photo_step(self, message, user):
        """Шаг в цепочке регистрации пользователя (загрузка фото профиля)
        :param Message message: Сообщение от пользователя
        :param User user: Текущий пользователь
        :raise TypeError: В случае, если в ТГ отправляется не фото
        """
        try:
            file_id = message.photo[-1].file_id
            file = self.bot.get_file(file_id)
            user_avatar = self.bot.download_file(file.file_path)
            save_path = os.path.join(settings.MEDIA_ROOT, 'images/avatars/')
            file_name = f"{user.chat_id}.jpg"
            complete_name = os.path.join(save_path, file_name)

            with open(complete_name, "wb") as img:
                img.write(user_avatar)

            self.bot.send_message(chat_id=message.chat.id, text='Фото установлено!')
            log_act(user, 'photo', complete_name)
            if user.profile.is_registered:
                self.show_user_profile(message)
            else:
                user.profile.is_registered = True
                user.profile.save()
                text = '<b>Поздравляем!!!</b> Ваша анкета успешно создана\n'
                text += 'Для просмотра текущего профиля укажите команду\n'
                text += '/profile или воспользуйтесь кнопкой "Мой профиль"'
                self.bot.send_message(
                    chat_id=message.chat.id,
                    text=text,
                    reply_markup=gen_main_markup(),
                    parse_mode='HTML'
                )
        except TypeError:
            message = self.bot.reply_to(
                message=message,
                text='Поддерживаемый формат: PNG/JPG\n(compress/сжатое)'
            )
            self.bot.register_next_step_handler(message, self.process_photo_step, user)