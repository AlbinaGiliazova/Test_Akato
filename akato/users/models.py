"""Модели пользователей."""

from django.db import models  # type:ignore
from django.contrib.auth.models import AbstractUser  # type:ignore
from django.core.validators import MaxLengthValidator  # type:ignore
from django.conf import settings  # type: ignore

from .validators import (validate_username, validate_email,
                         MaxLengthPasswordValidator)
from .constants import NAME_MAX_LENGTH, EMAIL_MAX_LENGTH, MAX_PASSWORD_LENGTH


class Role(models.TextChoices):
    """Роли пользователя."""

    USER = 'user', 'Пользователь'
    ADMIN = 'admin', 'Администратор'


def get_role_max_length():
    """Длина поля роли."""
    return max(len(role[0]) for role in Role.choices)


class UserWithShoppingCart(AbstractUser):
    """Модель пользователя с корзиной."""

    username = models.CharField(
        verbose_name='Логин',
        max_length=NAME_MAX_LENGTH,
        validators=(MaxLengthValidator,
                    validate_username),
        unique=True,
    )
    email = models.EmailField(
        verbose_name='Емайл',
        max_length=EMAIL_MAX_LENGTH,
        validators=(MaxLengthValidator,
                    validate_email),
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=NAME_MAX_LENGTH,
        validators=(MaxLengthValidator,),
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=NAME_MAX_LENGTH,
        validators=(MaxLengthValidator,),
    )
    password = models.CharField(
        max_length=MAX_PASSWORD_LENGTH,
        validators=(MaxLengthValidator,
                    MaxLengthPasswordValidator),
        verbose_name='Пароль',
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='users/',
        default=settings.DEFAULT_AVATAR,
        blank=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        choices=Role.choices,
        max_length=get_role_max_length(),
        validators=(MaxLengthValidator,),
        default=Role.USER,
    )
    shopping_cart = models.ManyToManyField(
        'products.Product',
        related_name='shopping_cart',
        verbose_name='Список покупок',
        blank=True,
        through='ShoppingCart',
    )

    class Meta:
        """Настройки."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        """Строковое представление."""
        return self.username

    @property
    def is_superuser_or_admin(self):
        """Является ли пользователь суперпользователем или администратором."""
        self.refresh_from_db()
        return self.is_superuser or self.role == Role.ADMIN


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        UserWithShoppingCart,
        on_delete=models.CASCADE,
        related_name='user_shopping_cart',
        verbose_name='Пользователь',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='product_shopping_cart',
        verbose_name='Товар',
    )

    class Meta:
        """Настройки модели."""

        constraints = (
            models.UniqueConstraint(fields=('user', 'product'),
                                    name='unique_shopping'),
        )
        verbose_name = 'Покупка'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        """Строковое представление."""
        return f'Список покупок: {self.user.username} - {self.product.name}'
