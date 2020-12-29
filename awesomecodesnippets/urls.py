from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/',include('allauth.urls')),
    path('', include("snippets.urls")),
    path('', include("comments.urls")),
]
