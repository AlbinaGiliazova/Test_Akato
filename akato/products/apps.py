"""Настройки приложения."""

from django.apps import AppConfig  # type:ignore


class RecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
    verbose_name = 'Товары'
