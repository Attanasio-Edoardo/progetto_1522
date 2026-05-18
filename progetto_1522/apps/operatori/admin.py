"""apps/operatori/admin.py"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Operatore


@admin.register(Operatore)
class OperatoreAdmin(UserAdmin):
    list_display  = ('username', 'get_full_name', 'email', 'specializzazione',
                     'stato_registrazione', 'is_active')
    list_filter   = ('stato_registrazione', 'specializzazione', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')

    fieldsets = UserAdmin.fieldsets + (
        ('Profilo Operatore', {
            'fields': (
                'telefono', 'specializzazione', 'titolo_studio',
                'curriculum_vitae', 'disponibilita', 'stato_registrazione'
            )
        }),
    )
