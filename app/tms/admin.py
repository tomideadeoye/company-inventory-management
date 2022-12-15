from django.contrib import admin
from django.utils.translation import gettext as _

from .models import Terminal, Group, TerminalLog 


admin.site.register(Terminal)
admin.site.register(Group)
admin.site.register(TerminalLog)
# admin.site.register(Component)
