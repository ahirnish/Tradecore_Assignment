from django.urls import path
from .views import LoginView, RegisterUsers, UserDetailView, ListUsersView, CreatePostView, ListPostsView, \
    ListPreferencesView, PreferenceDetailView, ListPostsByUserView, PostDetailView, LogoutView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name="auth-login"),
    path('auth/register/', RegisterUsers.as_view(), name="auth-register"),
    path('auth/logout/', LogoutView.as_view(), name="auth-logout"),
    path('user/all/', ListUsersView.as_view(), name="user-all"),
    path('user/<int:user_id>/', UserDetailView.as_view(), name="user-detail"),
    path('post/', CreatePostView.as_view(), name="post-create"),
    path('post/all/', ListPostsView.as_view(), name="post-list-all"),
    path('post/all/<username>/', ListPostsByUserView.as_view(), name="post-list-user"),
    path('post/<int:post_id>/', PostDetailView.as_view(), name="post-detail"),
    path('preference/all/', ListPreferencesView.as_view(), name="preference-list-all"),
    path('preference/<int:post_id>/', PreferenceDetailView.as_view(), name="preference-detail"),
]
