"""Модели."""

import re

from django.db import models  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore
from django.core.validators import (MaxLengthValidator,  # type: ignore
                                    MinValueValidator)
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
    image = models.ImageField(
        upload_to='products/images/categories/',
        verbose_name='Изображение',
    )

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
        related_name='subcategories',
        verbose_name='Категория',
    )
    image = models.ImageField(
        upload_to='products/images/subcategories/',
        verbose_name='Изображение',
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
    slug = models.SlugField(unique=True, max_length=MAX_SLUG_LENGTH,
                            validators=(MaxLengthValidator,
                                        validate_slug),
                            verbose_name='Слаг')
    price = models.DecimalField(
        max_digits=10,           # всего цифр (включая дробную часть)
        decimal_places=2,        # цифр после точки
        validators=[             # не даёт записать отрицательное значение
            MinValueValidator(0)
        ],
        default=0
    )
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
    
    def clean(self):
           # опционально: на уровне модели не позволяем больше 3 связей
           if self.pk and self.images.count() > 3:
               raise ValidationError("Максимум 3 изображения")
           

class ProductImage(models.Model):
       """Изображение товара."""
       
       product = models.ForeignKey(
           Product,
           related_name='images',
           on_delete=models.CASCADE
       )
       image = models.ImageField(upload_to='products/%Y/%m/%d/')
       order = models.PositiveSmallIntegerField(default=0)

       class Meta:
           unique_together = ('product', 'order')
           ordering = ['order']

       def __str__(self):
           return f"{self.product.name} — изображение №{self.order}"
