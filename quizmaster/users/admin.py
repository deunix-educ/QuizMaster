#
# encoding: utf-8
#from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff', 'role', 'color')


    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': ('role', 'color')
            }
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
            form = super().get_form(request, obj, **kwargs)
            is_superuser = request.user.is_superuser
            disabled_fields = []  # type: Set[str]

            if not is_superuser:
                disabled_fields |= {
                    'username',
                    'last_name',
                    'first_name',
                    'email',
                    'is_staff',
                    'is_active',
                    'groups',
                    'is_superuser',
                    'user_permissions',

                }
            # Prevent non-superusers from editing their own permissions
            if ( not is_superuser and obj is not None and obj == request.user ):
                disabled_fields |= {
                    'is_staff',
                    'is_superuser',
                    'is_active',
                    'groups',
                    'user_permissions',
                }

            for f in disabled_fields:
                if f in form.base_fields:
                    form.base_fields[f].disabled = True

            return form


admin.site.register(User, CustomUserAdmin)


