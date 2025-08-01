from django.contrib import admin
from .models import Comment
from snippets.models import CustomUser,Snippet
from  .models import Ratings
class CommentAdmin(admin.TabularInline):
    model=Comment


@admin.register(Snippet)
class CustomSnippetAdmin(admin.ModelAdmin):
    inlines=[CommentAdmin,]

admin.site.register(Ratings)
# admin.site.register(Comment)
