from abc import ABCMeta, abstractmethod, abstractproperty


class AbstractBot:
    __metaclass__ = ABCMeta

    def __init__(self, bot):
        self.bot = bot

    @abstractmethod
    def send_message_to_admin(self, message: str):
        """Команда по отправке сообщения админу в ТГ
        :param Message message: Текст сообщения
        """
        pass

    @abstractmethod
    def send_bug_message(self, message: str):
        """Команда /bug от пользователя
        Пользователь отправляет сообщение о некорректной работе бота.
        Сообщение логируется в консоль и файл
        :param Message message: Сообщение от пользователя
        """
        pass

    @abstractmethod
    def show_user_profile(self, message: str):
        """Команда /profile от пользователя
        При получении команды отображается текущий профиль пользователя.
        При отсутствии или незаконченной регистрации соответствующее уведомление.
        :param Message message: Сообщение от пользователя
        """
        pass

    @abstractmethod
    def get_user_avatar(self, user):
        """Получение изображения профиля текущего пользователя
        :param User user: Текущий пользователь бота
        :return: Аватар пользователя
        :rtype: bytes
        """
        pass


class AbstractRegistration:
    __metaclass__ = ABCMeta

    def __init__(self, bot):
        self.bot = bot

    @abstractmethod
    def start_message(self, message: str):
        """Команда /start от пользователя
        При получении команды начинается регистрация текущего пользователя.
        При завершенной регистрации команда отправляет приветствие.
        :param Message message: Сообщение от пользователя
        """
        pass

    @abstractmethod
    def callback_change_profile(self, call):
        """Изменение параметров текущего профиля пользователя
        Происходит переход к шагу цепочки параметра профиля как при регистрации.
        Дальнейший переход по цепочке не происходит (is_registered = True)
        :param call: Callback от inline-клавиши
        :raise User.DoesNotExist: Доступ в профиль при отсутствии регистрации
        """
        pass

    @abstractmethod
    def process_name_step(self, message: str, user):
        """Шаг в цепочке регистрации пользователя (указание имени)
        :param Message message: Сообщение от пользователя
        :param User user: Текущий пользователь
        """
        pass

    @abstractmethod
    def process_age_step(self, message, user):
        """Шаг в цепочке регистрации пользователя (указание возраста)
        :param Message message: Сообщение от пользователя
        :param User user: Текущий пользователь
        """
        pass

    @abstractmethod
    def process_sex_step(self, message, user):
        """Шаг в цепочке регистрации пользователя (указание пола)
        :param Message message: Сообщение от пользователя
        :param User user: Текущий пользователь
        """
        pass

    @abstractmethod
    def process_description_step(self, message, user):
        """Шаг в цепочке регистрации пользователя (указание описания профиля)
        :param Message message: Сообщение от пользователя
        :param User user: Текущий пользователь
        """
        pass

    @abstractmethod
    def process_photo_step(self, message, user):
        """Шаг в цепочке регистрации пользователя (загрузка фото профиля)
        :param Message message: Сообщение от пользователя
        :param User user: Текущий пользователь
        :raise TypeError: В случае, если в ТГ отправляется не фото
        """
        pass


class AbstractSearch:
    __metaclass__ = ABCMeta

    def __init__(self, bot):
        self.bot = bot

    @abstractmethod
    def callback_change_profile_search(self, call):
        """Изменение параметров поиска профилей пользователей
        :param call: Callback от inline-клавиши
        :raise User.DoesNotExist: Доступ к настройкам при отсутствии регистрации
        """
        pass

    @abstractmethod
    def get_user_profile_search(self, user):
        """Получение настроек для поиска пользователей
        :param User user: Текущий пользователь бота
        :return: Список текущих настроек для поиска пользователей
        :rtype: str
        """
        pass

    @abstractmethod
    def get_next_search_profile(self, client):
        """Получение очередного собеседника в соответствии с настройками поиска
        :param User client: Текущий пользователь бота
        :raise IndexError: Отсутствие пользователей согласно настройкам поиска
        """
        pass

    @abstractmethod
    def bot_message(self, message):
        """Сообщения с основной клавиатуры бота
        -Запрос текущего профиля
        -Настройки поиска пользователей
        -Поиск следующего пользователя в соответствии с настройками поиска
        :param Message message: Сообщение от пользователя
        """
        pass

    @abstractmethod
    def action(self, call):
        """Обработка действий: лайка и дизлайка
        :param call: Callback от inline-клавиши
        """
        pass

    @abstractmethod
    def get_next_like_profile(self, client):
        """Получение очередного собеседника, который поставил лайк
        :param User client: Текущий пользователь бота
        :raise IndexError: Отсутствие пользователей согласно настройкам поиска
        """
        pass

    @abstractmethod
    def show_user_profile_likes(self, client, user_id, flag, dop_text):
        """При получении команды отображается текущий профиль пользователя.
        При отсутствии или незаконченной регистрации соответствующее уведомление.
        :param User client: Текущий пользователь бота
        :param Str user_id: ID пользователя, который должен быть показан
        :param Str flag: Если '1' - по лайкам, '0' - поиск
        :param Str dop_text: Дополнительный текст
        """
        pass
