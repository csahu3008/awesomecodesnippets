from django.urls import path
from .views import AddComment,GetChildComments
urlpatterns=[
  path('add_comment/',AddComment.as_view(),name='add_comment') ,  
  path('child_comment/',GetChildComments.as_view(),name='child_comment')   
]