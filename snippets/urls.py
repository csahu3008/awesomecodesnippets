from django.urls import path,re_path
from .views import HomePage,CreateSnippet,DetailSnippet,DeleteSnippet,ListSnippet,MyStyleFile,TopContributers,TopLanguages,GetLangDetails,AddBookMark,DeleteBookMark,UserDetail,UpdateSnippet,BookMarkedSnippets

urlpatterns=[
    path('',HomePage.as_view(),name='home'),
    path('snippet/create/',CreateSnippet.as_view(),name='create_snippet'),
    path('snippet/detail/<int:pk>/',DetailSnippet.as_view(),name='detail_snippet'),
    path('snippet/delete/<int:pk>/',DeleteSnippet.as_view(),name='delete_snippet'),
    path('snippet/update/<int:pk>/',UpdateSnippet.as_view(),name='update_snippet'),
    path('snippet/list/',ListSnippet.as_view(),name='list_snippet'),
    path('snippet/user/',ListSnippet.as_view(),name='my_snippet'),
    path('bookmarks/',BookMarkedSnippets.as_view(),name='bookmark'),
    path('snippet/top_contributers/',TopContributers.as_view(),name='contributer'),
    path('languages/',TopLanguages.as_view(),name='languages'),
    re_path('^mystyle/',MyStyleFile.as_view(),name='change_style'),
    re_path('^language/detail/(?P<lang>[\w+]+)/',GetLangDetails.as_view(),name='detail_lang'),
    path('bookmark/add/',AddBookMark.as_view(),name='add_bookmark'),
    path('bookmark/delete/',DeleteBookMark.as_view(),name='delete_bookmark'),
    path('user/<int:pk>/',UserDetail.as_view(),name='user_detail'),

]