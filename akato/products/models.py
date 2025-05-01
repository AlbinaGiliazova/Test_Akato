"""Модели."""

import re

from django.db import models  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore
from django.core.validators import MaxLengthValidator  # type: ignore
from django.core.exceptions import ValidationError  # type: ignore

from .constants import (MAX_NAME_LENGTH, MAX_SLUG_LENGTH, 
                        MAX_SUBCATEGORY_NAME_LENGTH, MAX_CATEGORY_NAME_LENGTH)
from .querysets import AnnotatedRecipeQuerySet


def validate_slug(slug):
    """Проверка слага."""
    if len(slug) > MAX_SLUG_LENGTH:
        raise ValidationError(
            f'Длина слага не должна превышать '
            f'{MAX_SLUG_LENGTH} символов.'
        )
    if not re.fullmatch(r'^[-a-zA-Z0-9_]+$', slug):
        raise ValidationError(
            'Слаг содержит недопустимые символы.'
        )
    return slug


class Category(models.Model):
    """Модель категории."""

    name = models.CharField(max_length=MAX_CATEGORY_NAME_LENGTH,
                            validators=(MaxLengthValidator,),
                            verbose_name='Название',
                            unique=True)
    slug = models.SlugField(unique=True, max_length=MAX_SLUG_LENGTH,
                            validators=(MaxLengthValidator,
                                        validate_slug),
                            verbose_name='Слаг')

    class Meta:
        """Настройки."""

        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        """Строковое представление."""
        return self.name
  

class Subcategory(models.Model):
    """Модель подкатегории."""

    name = models.CharField(max_length=MAX_SUBCATEGORY_NAME_LENGTH,
                            validators=(MaxLengthValidator,),
                            verbose_name='Название',
                            unique=True)
    slug = models.SlugField(unique=True, max_length=MAX_SLUG_LENGTH,
                            validators=(MaxLengthValidator,
                                        validate_slug),
                            verbose_name='Слаг')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='category',
        verbose_name='Категория',
    )

    class Meta:
        """Настройки."""

        ordering = ('name',)
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'

    def __str__(self):
        """Строковое представление."""
        return self.name


User = get_user_model()


class Product(models.Model):
    """Модель товара."""

    name = models.CharField(max_length=MAX_NAME_LENGTH,
                            validators=(MaxLengthValidator,),
                            verbose_name='Название',
                            unique=True)
    image1 = models.ImageField(
        upload_to='products/images/',
        verbose_name='Изображение1',
    )
    image2 = models.ImageField(
        upload_to='products/images/',
        verbose_name='Изображение2',
    )
    image3 = models.ImageField(
        upload_to='products/images/',
        verbose_name='Изображение3',
    )
    text = models.TextField(verbose_name='Описание товара')
    subcategory = models.ForeignKey(Subcategory,
                                  on_delete=models.CASCADE,
                                  related_name='subcategory',
                                  verbose_name='Подкатегория',
                                  )
    pub_date = models.DateTimeField(verbose_name='Дата публикации',
                                    auto_now_add=True,
                                    db_index=True)
    short_url = models.TextField(verbose_name='Короткая ссылка',
                                 blank=True, unique=True)
    objects = AnnotatedRecipeQuerySet.as_manager()

    class Meta:
        """Настройки."""

        ordering = ('name',)
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        """Строковое представление."""
        return self.name
