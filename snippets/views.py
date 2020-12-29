import json
from django.shortcuts import render,reverse
from .models import Snippet,CustomUser,BookMark
from django.urls import reverse_lazy
from pygments.lexers import get_all_lexers
from django.core.exceptions import PermissionDenied,ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView,TemplateView,DetailView,DeleteView,ListView
from .form import SnippetCreateForm
from django.contrib.staticfiles.storage import staticfiles_storage
from pygments.styles import get_all_styles
from pygments.formatters import HtmlFormatter
from django.http import HttpResponse,JsonResponse
from awesomecodesnippets.settings import BASE_DIR
from django.core import serializers
from .form import StyleForm
from django.utils.decorators import method_decorator
from django.db.models import Q
from comments.models import Comment
from comments.forms import  CommentForm

class HomePage(TemplateView):
    template_name='home.html'
    
    def get_context_data(self,*args,**kwargs):
        LEXERS = [item for item in get_all_lexers() if item[1]]
        LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
        context=super().get_context_data(*args,**kwargs)
        context['latest']=Snippet.objects.all().order_by('-publication_date')
        context['top_contributers']=Snippet.get_top_contributers(self)[:5]
        
        languages_and_counts={}

        for lang,lang_name in LANGUAGE_CHOICES:
            count=Snippet.objects.filter(language=lang).count()
            languages_and_counts[lang]=count
        languages_and_counts=sorted(languages_and_counts.items(),key=lambda item:item[1],reverse=True)
        context['total_langs']=languages_and_counts[:5]

        return context

class ListSnippet(ListView):
    template_name='snippets/list.html'
    model=Snippet



class CreateSnippet(CreateView):
    form_class=SnippetCreateForm
    template_name='snippets/create.html'
    # success_url=reverse_lazy('home')
    def form_valid(self,form):
        s=form.save(commit=False)
        s.coder=self.request.user
        s.save()
        return super().form_valid(form)

class DetailSnippet(DetailView):
    template_name='snippets/detail.html'
    queryset=Snippet.objects.all()

    def get_context_data(self,**kwargs):
        print(self.get_object())
        bookmark_status=False
        try:
            if(BookMark.objects.get(user=self.request.user, snippet=self.get_object()) ):
                bookmark_status=True
        except ObjectDoesNotExist:
                bookmark_status=False

        context=super().get_context_data(**kwargs)
        context['form']=StyleForm
        context['bookmark_status']=bookmark_status
        # adding comments Snippet
        context['comments']=Comment.objects.filter(snippet=self.get_object(),parent=None).order_by('-date_commented')
        context['commentform']=CommentForm
        return context

class DeleteSnippet(DeleteView):
    template_name='snippets/delete.html'
    model=Snippet
    success_url=reverse_lazy('home')
    def dispatch(self,request,*args,**kwargs):
        my_obj=self.get_object()
        if(not my_obj.DoesNotExist()):
            raise PermissionDenied
        else:
            if(my_obj.coder==request.user):
                return super().dispatch(request,*args,**kwargs)
            else:
                raise PermissionDenied 

class MyStyleFile(TemplateView):
    def get(self,*args,**kwargs):
        url = staticfiles_storage.url('css/mystyle.css')
        if 'style' in self.request.GET:
            styles=self.request.GET['style']
        else:
            styles='monokai'
        style=HtmlFormatter(style=styles).get_style_defs()
        with open(str(BASE_DIR)+'/'+str(url),'w') as f:
            f.write(style)
        return HttpResponse(status=200)
    


class TopContributers(TemplateView):
    template_name='snippets/contributer.html'
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        query=Snippet.get_top_contributers(self)
        context['users']=query
        return context

class TopLanguages(TemplateView):
    template_name='snippets/languages.html'

    def get_context_data(self,**kwargs):
        LEXERS = [item for item in get_all_lexers() if item[1]]
        LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
        context=super().get_context_data(**kwargs)
        languages_and_counts={}
        for lang,lang_name in LANGUAGE_CHOICES:
            count=Snippet.objects.filter(language=lang).count()
            languages_and_counts[lang]=count
        languages_and_counts=sorted(languages_and_counts.items(),key=lambda item:item[1],reverse=True)
        context['total_langs']=languages_and_counts
        return context

class GetLangDetails(TemplateView):
    def get(self,*args,**kwargs):
        query=Snippet.objects.select_related('coder').filter(language=self.kwargs['lang'])
        data=serializers.serialize('json',query,fields=('title','publication_date','coder'),use_natural_foreign_keys=True,indent=2)
        return HttpResponse(data,content_type='application/json')


@method_decorator(csrf_exempt,name='dispatch')
class AddBookMark(TemplateView):
    def post(self,*args,**kwargs):
        snippet=Snippet.objects.get(id=self.request.POST['snippet_id'])
        BookMark.objects.create(snippet=snippet,user=self.request.user)

        return HttpResponse({"sucessfully Bookmarked":"True"},content_type='application/json')


@method_decorator(csrf_exempt,name='dispatch')
class DeleteBookMark(TemplateView):
    def post(self,*args,**kwargs):
        snippet=Snippet.objects.get(id=self.request.POST['snippet_id'])
        BookMark.objects.filter(snippet=snippet,user=self.request.user).delete()
        return HttpResponse({"sucessfully Deleted":"True"},content_type='application/json')