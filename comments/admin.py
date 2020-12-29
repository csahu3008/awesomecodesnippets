from django.contrib import admin
from .models import Comment
from snippets.models import CustomUser,Snippet

class CommentAdmin(admin.TabularInline):
    model=Comment


class CustomSnippetAdmin(admin.ModelAdmin):
    inlines=[CommentAdmin,]

admin.site.register(Snippet,CustomSnippetAdmin)
# admin.site.register(Comment)
