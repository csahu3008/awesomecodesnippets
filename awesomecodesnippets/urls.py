from django.contrib import admin
from django.urls import path,include
from django.conf.urls import handler404,handler500,handler403
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/',include('allauth.urls')),
    path('', include("snippets.urls")),
    path('', include("comments.urls")),
    path("ckeditor5/", include('django_ckeditor_5.urls'))
]
urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'snippets.views.handler404'
handler403 = 'snippets.views.handler403'
handler500 = 'snippets.views.handler500'
