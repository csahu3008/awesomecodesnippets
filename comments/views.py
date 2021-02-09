from django.shortcuts import render
from snippets.models import Snippet,CustomUser
from .models import Comment
from django.views.generic import TemplateView,View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .forms import CommentForm
from tagging.models import Tag,TaggedItem
from .models import Ratings
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy,reverse

class AddComment(TemplateView):

    # login_url='account_login'
    
    def post(self,*args,**kwargs):
        snip_obj=Snippet.objects.get(id=self.request.POST['snippet_id'])
        comment=CommentForm(self.request.POST).save(commit=False)
        comment.snippet=snip_obj
        comment.user=self.request.user
        comment.save()
        return HttpResponse({"comment_added":"success"})

@method_decorator(csrf_exempt,name='dispatch')
class AddReply(TemplateView):
    def post(self,*args,**kwargs):
        comment_parent_obj=None
        comment_parent_obj=Comment.objects.get(id=self.request.POST['parent_comment_id'])

        snip_obj=Snippet.objects.get(id=self.request.POST['snippet_id'])
        if CommentForm(self.request.POST).is_valid():
            comment=CommentForm(self.request.POST).save(commit=False)
            comment.snippet=snip_obj
            comment.parent=comment_parent_obj
            comment.user=self.request.user
            comment.save()
            return HttpResponse({"reply_added":"success"})
        else:
            print(CommentForm(self.request.POST).errors)
            return HttpResponse({"reply_error":"success"})



class GetChildComments(TemplateView):
    template_name='snippets/children_comments.html'
    
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        parent=Comment.objects.get(id=self.request.GET['comment_id'])
        childs=Comment.objects.filter(parent=parent)
        context['comments']=childs
        return context


class GetTaggedItems(TemplateView):
    template_name='snippets/tags.html'
    def get(self,*args,**kwargs):
        mytags=Tag.objects.get(name=self.kwargs['tag'])
        tagged_snippets=TaggedItem.objects.get_by_model(Snippet,mytags)
        print(tagged_snippets)
        return render(self.request,template_name=self.template_name,context={"tagged_snippets":tagged_snippets})

@method_decorator(csrf_exempt,name='dispatch')
class HelpfulOrNot(View):
    # template_name='base.html'
    def post(self,*args,**kwargs):
        
        snip_obj=Snippet.objects.get(id=self.request.POST['snippet_id'])
        p=Ratings.objects.create(point=self.request.POST['point'],snippet=snip_obj,user=self.request.user)

        return HttpResponse(p,content_type='application/json')
