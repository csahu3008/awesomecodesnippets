from rest_framework import routers
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from snippets.api_views import (
    SnippetViewSet, BookMarkViewSet, TopContributorsView, 
    LanguageStatsView, LanguageDetailView, UserDetailView,LanguageOptions
)
from comments.api_views import CommentViewSet, RatingViewSet, TaggedItemsView
from snippets.auth_views import (
    RegisterView, ChangePasswordView, UpdateProfileView,
    LogoutView, UserProfileView
)
from snippets.jwt_custom import CustomTokenObtainPairView

router = routers.DefaultRouter()
router.register(r'snippets', SnippetViewSet)
router.register(r'bookmarks', BookMarkViewSet, basename='bookmark')
router.register(r'comments', CommentViewSet)
router.register(r'ratings', RatingViewSet)

# Authentication endpoints
auth_urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('change-password/', ChangePasswordView.as_view(), name='auth_change_password'),
    path('update-profile/', UpdateProfileView.as_view(), name='auth_update_profile'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('profile/', UserProfileView.as_view(), name='auth_user_profile'),
]

urlpatterns = [
    path('', include(router.urls)),
    # Enable Django REST Framework's browsable API login/logout
    path('auth/', include(auth_urlpatterns)),
    path('top-contributors/', TopContributorsView.as_view(), name='api-top-contributors'),
    path('languages/', LanguageStatsView.as_view(), name='api-languages'),
    path('language/<str:lang>/', LanguageDetailView.as_view(), name='api-language-detail'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='api-user-detail'),
    path('tags/<str:tag>/', TaggedItemsView.as_view(), name='api-tagged-items'),
    path('language-options/', LanguageOptions, name='language-options'),
]