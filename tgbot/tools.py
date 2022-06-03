import logging
import functools
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings
from django.shortcuts import redirect
from .models import User, LogUsers, ActType

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


def check_is_registrations(func):
    """Проверка полной регистрации"""
    @functools.wraps(func)
    def wrapper(self, message, *args, **kwargs):
        try:
            user = User.objects.get(chat_id=message.chat.id)
            if user.profile.is_registered:
                result = func(self, message, *args, **kwargs)
                return result
            else:
                self.bot.send_message(
                    chat_id=message.chat.id,
                    text=("Вы не завершили регистрацию!\n"
                          "Воспользуйтесь командой:\n/start")
                )
        except User.DoesNotExist:
            self.bot.send_message(
                chat_id=message.chat.id,
                text="Вы не завели анкету!\nВоспользуйтесь командой:\n/start"
            )

    return wrapper


def log(func):
    """Декоратор для логирования исключений кода"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.exception(
                f"Exception raised in {func.__name__}. exception: {str(e)}")
            raise e

    return wrapper


@log
def send_email(message):
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = settings.EMAIL_RECEIVER
    msg['Subject'] = "БАГ РЕПОРТ \"NUCLEAR DATING BOT\""
    msg.attach(MIMEText(message, 'HTML'))

    try:
        # подключаемся к почтовому сервису
        smtp = smtplib.SMTP('smtp.mail.ru', 587)
        smtp.starttls()
        smtp.ehlo()
        # логинимся на почтовом сервере
        smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        # пробуем послать письмо
        smtp.sendmail(settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVER, msg.as_string().encode('utf-8'))
    except smtplib.SMTPException as err:
        print('Что - то пошло не так...')
        raise err
    finally:
        smtp.quit()


@log
def authorization_check(func):
    def decorator(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('/login')
        return func(request, *args, **kwargs)
    return decorator


def log_act(user, act_type, description=''):
    LogUsers.object.create(user=user, 
                        act_type=ActType.objects.get_or_create(type=act_type),
                        description=description)