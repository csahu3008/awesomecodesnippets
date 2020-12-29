from django.contrib import admin
from .models import CustomUser,Snippet,BookMark

admin.site.register(CustomUser)
# admin.site.register(Snippet)
admin.site.register(BookMark)