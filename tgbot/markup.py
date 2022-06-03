import functools
from .models import User, Profile, ProfileSearch, ProfileLikes
from telebot import types
from difflib import SequenceMatcher
from .tools import log


# @log
# def gen_markup_for_city(name, is_search):
#     """Генерация клавиатуры для списка городов
#     :param str name: Наименование города от пользователя
#     :param bool is_search: Генерация для профиля или поиска пользователей
#     :return: Inline-клавиатура
#     :rtype: InlineKeyboardMarkup
#     """
#     markup = types.InlineKeyboardMarkup()
#     markup.row_width = 2
#     cities = City.objects.all()
#
#     # print(cities, "-------------------------")
#
#     for city in cities:
#         if SequenceMatcher(None, name, city.name).ratio() > 0.8:
#             callback = 'search_' if is_search else ''
#             markup.add(types.InlineKeyboardButton(
#                 text=f"{city.name}, {city.region}",
#                 callback_data=f"city_{callback}{city.pk}"
#             ))
#     markup.add(types.InlineKeyboardButton(
#         text="🤷🏻‍♂️Города нет в списке",
#         callback_data="city_empty"
#     ))
#     return markup


@log
def gen_markup_for_profile(user):
    """Генерация клавиатуры для профиля пользователя
    :param User user: Текущий пользователь бота
    :return: Inline-клавиатура
    :rtype: InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton(
            text="👤Имя",
            callback_data="profile_edit_name"
        ),
        types.InlineKeyboardButton(
            text="🔢Возраст",
            callback_data="profile_edit_age"
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            text="🚹Пол",
            callback_data="profile_edit_sex"
        ),
        # types.InlineKeyboardButton(
        #     text="🏠Город",
        #     callback_data="profile_edit_city"
        # )
    )
    markup.add(
        types.InlineKeyboardButton(
            text="🖌️Описание",
            callback_data="profile_edit_description"
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            text="🖼Фото",
            callback_data="profile_edit_avatar"
        )
    )
    if user.profile.is_active:
        text_active = '✅Анкета активна'
    else:
        text_active = '⛔Анкета не активна'
    markup.add(
        types.InlineKeyboardButton(
            text=text_active,
            callback_data="profile_edit_active"
        )
    )
    return markup


@log
def gen_markup_for_profile_search():
    """Генерация клавиатуры для настройки параметров поиска пользователей
    :return: Inline-клавиатура
    :rtype: InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        text="Изменить возраст",
        callback_data="search_age"
    ))
    markup.add(types.InlineKeyboardButton(
        text="Изменить пол",
        callback_data="search_sex"
    ))
    # markup.add(types.InlineKeyboardButton(
    #     text="Изменить город",
    #     callback_data="search_city"
    # ))
    return markup


@log
def gen_markup_for_profile_search():
    """Генерация клавиатуры для настройки параметров поиска пользователей
    :return: Inline-клавиатура
    :rtype: InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        text="Изменить возраст",
        callback_data="search_age"
    ))
    markup.add(types.InlineKeyboardButton(
        text="Изменить пол",
        callback_data="search_sex"
    ))
    markup.add(types.InlineKeyboardButton(
        text="Сброс просмотренных профилей",
        callback_data="search_reset"
    ))
    return markup


@log
def gen_markup_for_age_search():
    """Генерация клавиатуры для диапазона возрастов искомых пользователей
    :return: Inline-клавиатура
    :rtype: InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    age_range = list(range(13, 55, 5))
    for index in range(0, 8, 2):
        first_diapason = f'{age_range[index]}-{age_range[index + 1]}'
        second_diapason = f'{age_range[index + 1]}-{age_range[index + 2]}'
        markup.add(
            types.InlineKeyboardButton(
                text=first_diapason,
                callback_data=f'search_age_{first_diapason}'
            ),
            types.InlineKeyboardButton(
                text=second_diapason,
                callback_data=f'search_age_{second_diapason}'
            )
        )
    markup.add(
        types.InlineKeyboardButton(
            text='50-100',
            callback_data='search_age_50-100'
        ),
        types.InlineKeyboardButton(
            text='Любой возраст',
            callback_data='search_age_13-100'
        )
    )
    return markup


@log
def gen_markup_for_sex_search():
    """Генерация клавиатуры для выбора пола искомых пользователей
    :return: Inline-клавиатура
    :rtype: InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton(
            text='🕺🏻',
            callback_data='search_sex_M'
        ),
        types.InlineKeyboardButton(
            text='💃🏻',
            callback_data='search_sex_W'
        ),
        types.InlineKeyboardButton(
            text='Другой',
            callback_data='search_sex_O'
        ),
        types.InlineKeyboardButton(
            text='Все',
            callback_data='search_sex_A'
        ),
    )
    return markup


@log
def gen_main_markup():
    """Генерация основной клавиатуры
    :return: Reply-клавиатура
    :rtype: ReplyKeyboardMarkup
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row_width = 2
    markup.add(
        types.KeyboardButton("🔍Поиск"),
        types.KeyboardButton("⚙Настройки поиска")
    )
    markup.add(
        types.KeyboardButton("😎Мой профиль")
    )
    markup.add(
        types.KeyboardButton("Посмотреть кому ты нравишься")
    )
    return markup

