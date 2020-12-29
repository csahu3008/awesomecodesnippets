from .models import Snippet,CustomUser
from django.db import models
from django.db.models import Count

class SnippetCustomManager(models.Manager):
    def get_top_contributers(self):
        return CustomUser.objects.annotate(score=Count('snippet')).order_by('score')