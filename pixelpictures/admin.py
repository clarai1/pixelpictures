from django.contrib import admin

from .models import User, Picture, Tag

admin.site.register(User)
admin.site.register(Picture)
admin.site.register(Tag)