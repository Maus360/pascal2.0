from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("blogs/", BlogListView.as_view(), name="blogs"),
    path("blog/create", login_required(BlogCreateView.as_view()), name="blog-create"),
    path("blogger/<int:pk>", BlogListbyAuthorView.as_view(), name="blogs-by-author"),
    path("blog/<int:pk>", BlogDetailView.as_view(), name="blog-detail"),
    path(
        "blog/<int:pk>/delete",
        login_required(BlogDeleteView.as_view()),
        name="blog-delete",
    ),
    path(
        "blog/<int:pk>/update",
        login_required(BlogUpdateView.as_view()),
        name="blog-update",
    ),
    path("authors/", AuthorListView.as_view(), name="authors"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LogInView.as_view(), name="login"),
    path("logout/", LogOutView.as_view(), name="logout"),
]
