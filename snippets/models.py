from django.db import models
from django.shortcuts import reverse
# formatter ,it knows how to output highloghted code in various formats
# highlighter it puts everything together to produce highlighted code in various formats
from markdown import markdown 
from django.utils.translation import gettext_lazy as _
from pygments import lexers,formatters,highlight
from pygments.styles import get_all_styles
from pygments.lexers import get_all_lexers,get_lexer_by_name
from django.db.models import Count
import datetime
from django.contrib.auth.models import AbstractUser
from tagging.fields import TagField

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])
from django_ckeditor_5.fields import CKEditor5Field

class CustomUser(AbstractUser):
    name=models.CharField(_("Name"),max_length=200)
    
    
    def natural_key(self):
        return (self.name,self.email,self.id)
   
    class Meta:
        unique_together=('name','email','id')
    
class Snippet(models.Model):
    title=models.CharField(max_length=500)
    # language=models.ForeignKey(Language,on_delete=models.CASCADE)
    coder=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    description=CKEditor5Field(blank=True,null=True)
    description_html=models.TextField(editable=False)
    code=models.TextField()
    highlighted_code=models.TextField(editable=False)
    tags=TagField()
    publication_date=models.DateTimeField(editable=False)
    updated_date=models.DateTimeField(editable=False)
    # added to check the functionalities
    
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)
   
   
    class Meta:
        ordering=['-publication_date']

    def __str__(self):
        return self.title
    
    def get_top_contributers(self):
        return CustomUser.objects.annotate(score=Count('snippet')).order_by('-score')

    def get_absolute_url(self):
        return reverse('detail_snippet',args=[str(self.pk)])

    def highlight(self):
        return highlight(self.code,get_lexer_by_name(self.language,stripall=True,encoding="utf-8"),formatters.HtmlFormatter(style=self.style,linenos=True,cssclass=self.style))
    
    def save(self,force_insert=False,force_update=False):
        if not self.id:
            self.publication_date=datetime.datetime.now()
        
        self.updated_date=datetime.datetime.now()
        self.description_html=markdown(self.description)
        self.highlighted_code=self.highlight()
        super(Snippet,self).save(force_insert,force_update)


class BookMark(models.Model):
    snippet=models.ForeignKey(Snippet,on_delete=models.CASCADE)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    date_bookmarked=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.snippet.title+ " was bookmarked by "+self.user.email
