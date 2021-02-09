from django.urls import path,re_path
from .views import AddComment,GetChildComments,AddReply,GetTaggedItems,HelpfulOrNot
urlpatterns=[
  path('add_comment/',AddComment.as_view(),name='add_comment') ,  
  path('add_reply/',AddReply.as_view(),name='add_reply') ,  
  path('child_comment/',GetChildComments.as_view(),name='child_comment')  ,
  re_path('^tags/(?P<tag>[\w+]+)/',GetTaggedItems.as_view(),name='tag'),
    path('rate/',HelpfulOrNot.as_view(),name='rating') ,  
 
] 