import os
from .bot import Bot
from .tools import log, check_is_registrations, log_act
from django.conf import settings
from .models import User, Profile, ProfileSearch, ProfileLikes
from .markup import *
from django.utils.timezone import now
from .abstract import AbstractSearch


class Search(AbstractSearch, Bot):

    @staticmethod
    def _give_username_or_id(user):
        if user.username:
            return f'Ник пользователя: @{user.username}'
        else:
            return f'Ссылка на пользователя: <a href="tg://user?id={user.chat_id}">{user.profile.name}</a>'

    @log
    def callback_change_profile_search(self, call):
        """Изменение параметров поиска профилей пользователей
        :param call: Callback от inline-клавиши
        :raise User.DoesNotExist: Доступ к настройкам при отсутствии регистрации
        """
        try:
            user = User.objects.get(chat_id=call.from_user.id)
            text = markup = None

            if call.data == 'search_age':
                text = '<b>Выберите возрастной диапозон</b>: '
                markup = gen_markup_for_age_search()
                self.bot.answer_callback_query(call.id)
            if call.data.startswith('search_age_'):
                user.profilesearch.age = call.data.split('_')[-1]
                user.profilesearch.unviewed.clear()
                user.profilesearch.save()
                text = self.get_user_profile_search(user)
                markup = gen_markup_for_profile_search()

            if call.data == 'search_sex':
                text = 'Выберите пол собеседника'
                markup = gen_markup_for_sex_search()
            if call.data.startswith('search_sex_'):
                user.profilesearch.sex = call.data.split('_')[-1]
                user.profilesearch.unviewed.clear()
                user.profilesearch.save()
                text = self.get_user_profile_search(user)
                markup = gen_markup_for_profile_search()

            if call.data == 'search_reset':
                text = 'Сброс просмотренных профилей'
                markup = gen_markup_for_profile_search()
                user.profilesearch.unviewed.clear()
                user.profilesearch.viewed.clear()
                user.profilesearch.save()

            self.bot.edit_message_text(
                text=text,
                chat_id=call.from_user.id,
                message_id=call.message.message_id,
                parse_mode='HTML'
            )
            self.bot.edit_message_reply_markup(
                chat_id=call.from_user.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            self.bot.answer_callback_query(call.id)
            return

        except User.DoesNotExist:
            self.bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=call.message.message_id,
                text="Вы не завели анкету!\nВоспользуйтесь командой:\n/start"
            )

    @log
    def get_user_profile_search(self, user):
        """Получение настроек для поиска пользователей
        :param User user: Текущий пользователь бота
        :return: Список текущих настроек для поиска пользователей
        :rtype: str
        """
        text = '<i>Ваши настройки для поиска собеседника</i>: \n\n'
        text += f'<b>🔢Возраст: </b>{user.profilesearch.age}\n'
        if user.profilesearch.sex == 'M':
            text += '<b>🚹Пол: </b> Мужчина\n'
        elif user.profilesearch.sex == 'W':
            text += '<b>🚺Пол: </b> Женщина\n'
        elif user.profilesearch.sex == 'O':
            text += '<b>Пол: </b> Другой\n'
        elif user.profilesearch.sex == 'A':
            text += '<b>Пол: </b> Все\n'

        text += '\nВы можете изменить настройки поиска: '

        return text

    @log
    def get_next_search_profile(self, client):
        """Получение очередного собеседника в соответствии с настройками поиска
        :param User client: Текущий пользователь бота
        :raise IndexError: Отсутствие пользователей согласно настройкам поиска
        """
        try:
            user_id = client.profilesearch.unviewed.pop()
            if client.profile.is_active and client.profile.is_registered:
                self.show_user_profile_likes(client, user_id, '0', '')
            elif not client.profile.is_active:
                self.bot.send_message(
                    chat_id=client.chat_id,
                    text='\n Ваш профиль не активный, сделайте его активным',
                    parse_mode='HTML'
                )
            elif not client.profile.is_registered:
                self.bot.send_message(
                    chat_id=client.chat_id,
                    text='\n Вы не прошли регистрацию /start',
                    parse_mode='HTML'
                )

            client.profilesearch.viewed.append(user_id)
            client.profilesearch.save()
        except IndexError:
            text = 'К сожалению, мы никого <b>не нашли</b>\n'
            text += 'Попробуйте изменить настройки поиска'
            self.bot.send_message(
                chat_id=client.chat_id,
                text=text,
                parse_mode='HTML'
            )

    @check_is_registrations
    @log
    def bot_message(self, message):
        """Сообщения с основной клавиатуры бота
        -Запрос текущего профиля
        -Настройки поиска пользователей
        -Поиск следующего пользователя в соответствии с настройками поиска
        :param Message message: Сообщение от пользователя
        """
        try:
            if message.chat.type == 'private': # что это значит ?
                if message.text == '😎Мой профиль':
                    user = User.objects.get(chat_id=message.chat.id)
                    log_act(user, 'press_my_prof')
                    self.show_user_profile(message)
                if message.text == '⚙Настройки поиска':
                    user = User.objects.get(chat_id=message.chat.id)
                    log_act(user, 'press_search_settings')
                    self.bot.send_message(
                        chat_id=user.chat_id,
                        text=self.get_user_profile_search(user),
                        reply_markup=gen_markup_for_profile_search(),
                        parse_mode='HTML'
                    )
                if message.text == 'Посмотреть кому ты нравишься':
                    client = User.objects.get(chat_id=message.from_user.id)
                    log_act(client, 'press_settings')
                    self.get_next_like_profile(client)
                if message.text == '🔍Поиск':
                    client = User.objects.get(chat_id=message.chat.id)
                    if not client.profilesearch.unviewed:
                        start_age, end_age = map(
                            int,
                            client.profilesearch.age.split('-')
                        )
                        if client.profilesearch.sex == 'A':
                            list_users_for_search = User.objects.filter(
                                profile__age__range=(start_age, end_age),
                                profile__is_active=True,
                                profile__is_registered=True,
                            ).exclude(chat_id=client.chat_id).order_by('?')
                        else:
                            list_users_for_search = User.objects.filter(
                                profile__age__range=(start_age, end_age),
                                profile__sex=client.profilesearch.sex,
                                profile__is_active=True,
                                profile__is_registered=True,
                            ).exclude(chat_id=client.chat_id).order_by('?')

                        for user in list_users_for_search:
                            if (user.chat_id not in client.profilesearch.viewed and
                                    user.chat_id not in client.profilesearch.unviewed):
                                client.profilesearch.unviewed.append(user.chat_id)
                        client.profilesearch.save()

                    self.get_next_search_profile(client)
        except User.DoesNotExist:
            self.bot.send_message(
                chat_id=message.chat.id,
                text="Вы не завели анкету!\nВоспользуйтесь командой:\n/start"
            )

    @log
    def action(self, call):
        """
        Обработка действий: лайка и дизлайка
        :param call: Callback от inline-клавиши
        """
        pref, flag, user_id = call.data.split()
        # user_id = int(user_id)
        client = User.objects.get(chat_id=call.from_user.id)
        # print('------------', user_id)
        user = User.objects.get(chat_id=user_id)
        client.last_use = now()
        if not client.profile.is_registered:
            self.bot.send_message(
                chat_id=client.chat_id,
                text='Пройдите регистрацию',
                parse_mode='HTML'
            )
        elif not client.profile.is_active:
            self.bot.send_message(
                chat_id=client.chat_id,
                text="Вы сделали вашу анкету неактивной, сделайте ее активной"
            )
        elif pref == 'action_like':
            if user_id in client.profilelikes.unviewed:
                text = 'Это взаимно !!!\n'
                markup = types.InlineKeyboardMarkup()
                markup.row_width = 1
                markup.add(
                    types.InlineKeyboardButton(
                        text='💌 Написать\n',
                        url=f'tg://user?id={user.chat_id}'
                    )
                )
                self.bot.send_photo(
                    chat_id=client.chat_id,
                    photo=self.get_user_avatar(user),
                    caption=text + self._give_username_or_id(user),
                    reply_markup=markup,
                    parse_mode='HTML'
                )

                markup = types.InlineKeyboardMarkup()
                markup.row_width = 1
                markup.add(
                    types.InlineKeyboardButton(
                        text='💌 Написать\n',
                        url=f'tg://user?id={client.chat_id}'
                    )
                )
                self.bot.send_photo(
                    chat_id=user.chat_id,
                    photo=self.get_user_avatar(client),
                    caption=text + self._give_username_or_id(client),
                    reply_markup=markup,
                    parse_mode='HTML'
                )
                client.profilelikes.unviewed.remove(user_id)
                client.profilelikes.viewed.append(user_id)
                user.profilelikes.viewed.append(client.chat_id)

                user.profilelikes.save()
                client.profilelikes.save()

            elif user_id in client.profilelikes.viewed:
                text = 'У вас уже был мэтч\n'
                markup = types.InlineKeyboardMarkup()
                markup.row_width = 1
                markup.add(
                    types.InlineKeyboardButton(
                        text='💌 Написать\n',
                        url=f'tg://user?id={user.chat_id}'
                    )
                )
                self.bot.send_photo(
                    chat_id=client.chat_id,
                    photo=self.get_user_avatar(user),
                    caption=text + self._give_username_or_id(user),
                    reply_markup=markup,
                    parse_mode='HTML'
                )
            else:
                if client.chat_id in user.profilelikes.unviewed + user.profilelikes.viewed:
                    text = 'Вы уже лайкали этого пользователя\n'
                    self.bot.send_message(
                        chat_id=client.chat_id,
                        text=text,
                        parse_mode='HTML'
                    )
                else:
                    user.profilelikes.unviewed.append(client.chat_id)
                    user.profilelikes.save()

                    self.bot.send_message(
                        chat_id=user.chat_id,
                        text='Вас лайкнули !!!',
                        parse_mode='HTML'
                    )
                    if flag == '0':
                        self.get_next_search_profile(client)
                    else:
                        self.get_next_like_profile(client)
        elif pref == 'action_dislike':
            if user_id in client.profilelikes.unviewed:
                client.profilelikes.unviewed.remove(user_id)
            if client.chat_id in user.profilelikes.unviewed:
                user.profilelikes.unviewed.remove(client.chat_id)
            if client.chat_id in user.profilelikes.viewed:
                user.profilelikes.viewed.remove(client.chat_id)
            self.bot.send_message(
                chat_id=client.chat_id,
                text='Тогда смотрим дальше...',
                parse_mode='HTML'
            )
            client.profilelikes.save()
            user.profilelikes.save()
            if flag == '0':
                self.get_next_search_profile(client)
            else:
                self.get_next_like_profile(client)

    @log
    def get_next_like_profile(self, client):
        """Получение очередного собеседника, который поставил лайк
        :param User client: Текущий пользователь бота
        :raise IndexError: Отсутствие пользователей согласно настройкам поиска
        """
        try:
            user_id = client.profilelikes.unviewed[0]
            # print(user_id)
            dop_text = f'<b>Этот человек лайкнул вас</b>\n'
            self.show_user_profile_likes(client, user_id, '1', dop_text)

        except IndexError:
            text = 'К сожалению, мы никого <b>не нашли</b>\n'
            text += 'Попробуйте подождать, кто-нибудь да лайкнет'
            self.bot.send_message(
                chat_id=client.chat_id,
                text=text,
                parse_mode='HTML'
            )

    @log
    def show_user_profile_likes(self, client, user_id, flag, dop_text):
        """При получении команды отображается текущий профиль пользователя.
        При отсутствии или незаконченной регистрации соответствующее уведомление.
        :param User client: Текущий пользователь бота
        :param Str user_id: ID пользователя, который должен быть показан
        :param Str flag: Если '1' - по лайкам, '0' - поиск
        :param Str dop_text: Дополнительный текст
        """
        user = User.objects.get(chat_id=user_id)
        text = f'<b>👤Имя: </b>{user.profile.name}\n'
        text += f'<b>🔢Возраст: </b>{user.profile.age}\n'
        if user.profile.sex == 'M':
            text += '<b>🚹Пол: </b> Мужчина\n'
        elif user.profile.sex == 'W':
            text += '<b>🚺Пол: </b> Женщина\n'
        elif user.profile.sex == 'O':
            text += '<b>Пол: </b> Не определён\n'

        text += f'<b>🖌️Описание: </b>{user.profile.description}\n\n'
        text += dop_text
        markup = types.InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(
            types.InlineKeyboardButton(
                text='👍🏻',
                callback_data=f'action_like {flag} {str(user_id)}'
            ),
            types.InlineKeyboardButton(
                text='👎🏻',
                callback_data=f'action_dislike {flag} {str(user_id)}'
            )
        )
        self.bot.send_photo(
            chat_id=client.chat_id,
            photo=self.get_user_avatar(user),
            caption=text,
            reply_markup=markup,
            parse_mode='HTML'
        )