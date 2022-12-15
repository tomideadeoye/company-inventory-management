from django.contrib import admin
from django.utils.translation import gettext as _
from .models import User, Token


admin.site.register(User)
admin.site.register(Token)
