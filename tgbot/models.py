from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.forms import CharField
from django.utils import timezone

max_length_id = 15


class User(models.Model):
    chat_id = models.CharField(
        max_length=max_length_id,
        primary_key=True,
        verbose_name='Chat id пользователя',
    )
    first_name = models.CharField(
        max_length=128,
        verbose_name='Имя пользователя'
    )
    username = models.CharField(
        null=True,
        blank=True,
        max_length=128,
        verbose_name='Ник пользователя'
    )
    creation_date = models.DateTimeField(
        verbose_name='Дата создания',
        # default=timezone.now(),
        auto_now=True,
    )
    last_use = models.DateTimeField(
        verbose_name='Дата последнего использования',
        # default=timezone.now(),
        auto_now=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.chat_id)


# class City(models.Model):
#     name = models.CharField(
#         max_length=200,
#         blank=True,
#         verbose_name='Наименование н/п'
#     )
#     region = models.CharField(
#         max_length=200,
#         blank=True,
#         verbose_name='Регион'
#     )
#
#     class Meta:
#         verbose_name = 'Город'
#         verbose_name_plural = 'Города'
#
#     def __str__(self):
#         return str(f'{self.name}, {self.region}')


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    name = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Имя'
    )
    age = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Возраст'
    )
    sex = models.CharField(
        max_length=1,
        blank=True,
        verbose_name='Пол'
    )
    # city = models.ForeignKey(
    #     City,
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     blank=True
    # )
    description = models.CharField(
        max_length=400,
        blank=True,
        verbose_name='О себе'
    )
    is_registered = models.BooleanField(
        default=False,
        verbose_name='Анкета зарегистрирована?'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Анкета активна?'
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return str(self.user)


class ProfileSearch(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    age = models.CharField(
        max_length=10,
        default='13-100',
        verbose_name='Возраст собеседника'
    )
    sex = models.CharField(
        max_length=1,
        default='A',
        verbose_name='Пол собеседника'
    )
    # city = models.ForeignKey(
    #     City,
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     blank=True
    # )

    unviewed = ArrayField(
        models.CharField(max_length=max_length_id,),
        default=list,
        blank=True
    )
    viewed = ArrayField(
        models.CharField(max_length=max_length_id,),
        default=list,
        blank=True
    )

    class Meta:
        verbose_name = 'Профиль для поиска'
        verbose_name_plural = 'Профили для поиска'

    def __str__(self):
        return str(self.user)


class ProfileLikes(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    unviewed = ArrayField(
        models.CharField(max_length=max_length_id,),
        default=list,
        blank=True,
        verbose_name='не просмотренные лайки',
    )
    viewed = ArrayField(
        models.CharField(max_length=max_length_id,),
        default=list,
        blank=True,
        verbose_name='взаимные лайки',
    )

    class Meta:
        verbose_name = 'Профиль для лайков'
        verbose_name_plural = 'Профили для лайков'

    def __str__(self):
        return str(self.user)

class ActType(models.Model):
    type = models.CharField(
        max_length=40,
        verbose_name='Название типа действия',
        primary_key=True,)
        
class LogUsers(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    log_date = models.DateTimeField(
        verbose_name='Дата совершения действия',
        auto_now=True,
    )
    act_type = models.ForeignKey(
        ActType,
        on_delete=models.CASCADE,
        verbose_name='Название типа действия',
    )
    description = models.CharField(
        max_length=400,
        verbose_name='Дополнительные данные о действии',
        blank=True,)
        