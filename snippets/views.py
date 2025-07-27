import json
from django.shortcuts import render,reverse
from .models import Snippet,CustomUser,BookMark
from django.urls import reverse_lazy
from pygments.lexers import get_all_lexers
from django.core.exceptions import PermissionDenied,ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView,TemplateView,DetailView,DeleteView,ListView,UpdateView
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
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.list import MultipleObjectMixin
from tagging.models import Tag,TaggedItem
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy,reverse

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
            
        
        context['tags']=sorted(Tag.objects.usage_for_queryset(Snippet.objects.all(),counts=True,min_count=None),key=lambda x:-x.count)
        
        # print(context['tags'])
        return context

class ListSnippet(ListView):
    template_name='snippets/list.html'
    model=Snippet
    paginate_by=6
    def get_queryset(self):
        if self.request.path=='/snippet/user/' and self.request.user.is_authenticated==True:
            return super().get_queryset().filter(coder=self.request.user)
        elif self.request.path=='/snippet/user/':
             raise PermissionDenied
        return super().get_queryset()
    

class BookMarkedSnippets(LoginRequiredMixin,ListView):
    template_name='snippets/bookmarks.html'
    model=BookMark
    paginate_by=5
    def get_queryset(self):
            return super().get_queryset().filter(user=self.request.user)


class UpdateSnippet(LoginRequiredMixin,UpdateView):
    template_name='snippets/update.html'
    model=Snippet
    fields=['title','description','code']
    login_url=reverse_lazy('account_login')
    


class CreateSnippet(LoginRequiredMixin,CreateView):
    form_class=SnippetCreateForm
    template_name='snippets/create.html'
    login_url=reverse_lazy('account_login')
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
        bookmark_status=False
        
        if self.request.user.is_authenticated==True:
            user_status=True        
            try:
                if(BookMark.objects.get(user=self.request.user, snippet=self.get_object()) ):
                    bookmark_status=True
            except ObjectDoesNotExist:
                    bookmark_status=False
        else:
            user_status=False        


        context=super().get_context_data(**kwargs)
        context['form']=StyleForm
        context['bookmark_status']=bookmark_status
        context['user_logged_in']=user_status
        # adding comments Snippet
        context['comments']=Comment.objects.filter(snippet=self.get_object(),parent=None).order_by('-date_commented')
        context['commentform']=CommentForm
        return context

class DeleteSnippet(LoginRequiredMixin,DeleteView):
    template_name='snippets/delete.html'
    model=Snippet
    login_url=reverse_lazy('account_login')
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
    template_name='lang/lang_detail.html'
    context_object_name='lang'
    
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        query=Snippet.objects.select_related('coder').filter(language=kwargs['lang'])
        total=query.count()
        page = self.request.GET.get('page')
        paginator=Paginator(query,6)
        
        try:
            context['lang_snippets']= paginator.page(page)
        except PageNotAnInteger:
            context['lang_snippets'] = paginator.page(1)
        except EmptyPage:
            context['lang_snippets'] = paginator.page(paginator.num_pages)

        context['page']=page
        context['total_snippets']=total
        print(context)
        
        return context


@method_decorator(csrf_exempt,name='dispatch')
class AddBookMark(TemplateView):
    def post(self,*args,**kwargs):
        snippet=Snippet.objects.get(id=self.request.POST['snippet_id'])
        BookMark.objects.create(snippet=snippet,user=self.request.user)

        return HttpResponse(status=200,content_type='application/json')


@method_decorator(csrf_exempt,name='dispatch')
class DeleteBookMark(TemplateView):
    def post(self,*args,**kwargs):
        snippet=Snippet.objects.get(id=self.request.POST['snippet_id'])
        BookMark.objects.filter(snippet=snippet,user=self.request.user).delete()
        return HttpResponse(status=200,content_type='application/json')


class UserSnippetsMixin:
    model=Snippet
    def get_context_data(self,**kwargs):
        context={}
        snippets=Snippet.objects.filter(coder=kwargs['object']).order_by('-updated_date')
        
        paginator=Paginator(snippets,5)
        page = self.request.GET.get('page')
        
        context['user_info']=kwargs['object']
        context['total_snippets']=snippets.count()

        try:
            user_snippets = paginator.page(page)
            context['user_snippets']=user_snippets
        except PageNotAnInteger:
                # If page is not an integer deliver the first page
            user_snippets = paginator.page(1)
            context['user_snippets']=user_snippets

        except EmptyPage:
            # If page is out of range deliver last page of results
            user_snippets = paginator.page(paginator.num_pages)
            context['user_snippets']=user_snippets
       
        context['page']=page
        return context

class UserDetail(UserSnippetsMixin,DetailView):
    template_name='account/user_detail.html'
    context_object_name='user'
    model=CustomUser
    
    def get_context_data(self,**kwargs):
        # print("This was called 1 ")
        context=super().get_context_data(**kwargs)
        # print("This was called 2")
        return context

    # the printing order is 1 ,3 ,2


def handler404(request, exception, template_name="404.html"):
    response = render(request,template_name)
    response.status_code = 404
    return response

def handler500(request,template_name="500.html"):
    response = render(request,template_name)
    response.status_code = 500
    return response


def handler403(request,template_name="403.html"):
    response = render(request,template_name)
    response.status_code = 403
    return response