from django.contrib import admin
from django.urls import path,include
from django.conf.urls import handler404,handler500,handler403



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/',include('allauth.urls')),
    path('', include("snippets.urls")),
    path('', include("comments.urls")),
]

handler404 = 'snippets.views.handler404'
handler403 = 'snippets.views.handler403'
handler500 = 'snippets.views.handler500'
