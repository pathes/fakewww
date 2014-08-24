from django.contrib import admin
from .models import *


class DomainAdmin(admin.ModelAdmin):
    model = Domain


class WebpageAdmin(admin.ModelAdmin):
    model = Webpage


admin.site.register(Domain, DomainAdmin)
admin.site.register(Webpage, WebpageAdmin)
