from django.contrib import admin  # type: ignore
from django.contrib.auth.models import Group  # type: ignore
from rest_framework.authtoken.admin import TokenAdmin  # type: ignore
from rest_framework.authtoken.models import Token  # type: ignore

from .models import Category, Subcategory, Product
from users.models import ShoppingCart


TokenAdmin.verbose_name = 'Токен'
TokenAdmin.verbose_name_plural = 'Токены'
Token._meta.verbose_name = 'Токен'
Token._meta.verbose_name_plural = 'Токены'
admin.site.site_header = 'Административная панель'
admin.site.site_title = 'Административная панель'
admin.site.index_title = 'Административная панель'


class BaseAdmin(admin.ModelAdmin):
    """Базовый администратор."""

    actions = ('change_selected',
               'delete_selected')
    empty_value_display = '-пусто-'


class ProductAdmin(BaseAdmin):
    """Регистрация товаров."""

    list_display = ('name',
                    'image1',
                    'image2',
                    'image3',
                    'text',
                    'short_url')
    fields = ('name',
              'image1',
              'image2',
              'image3',
              'text',
              'subcategory',
              'short_url')
    list_filter = ('subcategory',)
    search_fields = ('name',)
    verbose_name = 'Товар'
    verbose_name_plural = 'Товары'


class SubcategoryAdmin(BaseAdmin):
    """Регистрация подкатегорий."""

    list_display = ('name', 'slug', 'category__name', 'image')
    fields = ('name', 'slug', 'category__id', 'image')
    search_fields = ('name', 'category__name')
    verbose_name = 'Подкатегория'
    verbose_name_plural = 'Подкатегории'


class CategoryAdmin(BaseAdmin):
    """Регистрация категорий."""

    list_display = ('name', 'slug', 'image')
    fields = ('name', 'slug', 'image')
    search_fields = ('name',)
    verbose_name = 'Категория'
    verbose_name_plural = 'Категории'   


class ShoppingCartAdmin(BaseAdmin):
    """Регистрация списка покупок."""

    list_display = ('user', 'product')
    fields = ('user', 'product')
    search_fields = ('user__username',)
    verbose_name = 'Список покупок'
    verbose_name_plural = 'Список покупок'


admin.site.register(Subcategory, SubcategoryAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.unregister(Group)
