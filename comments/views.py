from django.shortcuts import render
from snippets.models import Snippet,CustomUser
from .models import Comment
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .forms import CommentForm
# @method_decorator(csrf_exempt,name='dispatch')
class AddComment(TemplateView):
    def post(self,*args,**kwargs):
        comment_parent_obj=None
        if 'parent_comment_id' in self.request.POST:
           print("The Parent Exists ")
           comment_parent_obj=Comment.objects.get(id=self.request.POST['parent_comment_id'])
           print("Parent Comment ID is ",comment_parent_obj)
        else:
           print("The Parent Does Not Exist ")

        snip_obj=Snippet.objects.get(id=self.request.POST['snippet_id'])
        comment=CommentForm(self.request.POST).save(commit=False)
        comment.snippet=snip_obj
        comment.parent=comment_parent_obj
        comment.user=self.request.user
        comment.save()
        return HttpResponse({"comment_added":"success"})


class GetChildComments(TemplateView):
    template_name='snippets/children_comments.html'
    
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        parent=Comment.objects.get(id=self.request.GET['comment_id'])
        childs=Comment.objects.filter(parent=parent)
        context['comments']=childs
        return context