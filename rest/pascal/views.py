from .models import *
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.contrib.auth.hashers import check_password
from .serializers import *
from .models import User


class BlogViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Blog.objects.all()
    serializer_class = BlogSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer


class Auth(APIView):
    renderer_classes = (JSONRenderer,)

    def post(self, request, *args, **kwargs):
        print(kwargs)

        content = {
            "auth": str(
                auth(request.POST.get("username"), request.POST.get("password"))
            )
        }
        return Response(content)


def auth(username, password):
    users = User.objects.all()
    for user in users:
        if user.username == username:
            if check_password(password, user.password):
                return user.id
            return False
    return None
