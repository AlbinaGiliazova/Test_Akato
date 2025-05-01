from django.contrib import admin  # type: ignore
from django.contrib.auth.admin import UserAdmin  # type: ignore

from users.models import UserWithShoppingCart

UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('avatar',
                                 'role',
                                 )}),
)
UserAdmin.list_display += (
    'avatar',
    'role',
)
UserAdmin.search_fields = ('email', 'username')
UserAdmin.verbose_name = 'Пользователь'
UserAdmin.actions += ('change_selected',
                      'delete_selected')

admin.site.register(UserWithShoppingCart, UserAdmin)
