from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django import forms
from django.utils import timezone

from .models import MyUser
from datetime import datetime
import requests

server_url = settings.SERVER_URL


def my_authenticate(username, password):
    user = requests.post(
        server_url + "auth/", data={"username": username, "password": password}
    ).json()
    if user["auth"] == "False":
        return False
    elif user["auth"] == "None":
        raise MyUser.DoesNotExist()
    else:
        user = requests.get(server_url + f"user/{user['auth']}").json()
        return user


class MyBackend(object):
    def authenticate(self, request, **kwargs):
        """
        kwargs will receive the python dict that may contain 
        username & password to authenticate which will be 
        received from the Custom admin site.
        """
        try:
            username = kwargs["username"]
            password = kwargs["password"]

            user = my_authenticate(username, password)
            if not user:
                return None
            # print(my_authenticate(username, password))
            """
            Check if the user exist in the django_auth_user 
            table, if not then UserNotExist exception will  
            be raised automatically and user will be added 
            (with or without password) in the exception 
            handling block
            """

            # Check if the user exist in the database, if it exist in the
            # database, auth_user will not be updated and exception will not be raised
            user = MyUser(**user)

        except KeyError as e:
            raise forms.ValidationError(("Programming Error"))

        except MyUser.DoesNotExist:
            """
            Add the username to the django_auth_users so 
            that login session can keep track of it. 
            Django Admin is heavily coupled with the 
            Django User model for the user instane in the 
            django_auth_users table. The request object then 
            map the request.user feild to this object of the
            data model.
            """
            # user = MyUser.objects.create_user(
            # username,
            # make_password(password, hasher="pbkdf2_sha256"),
            # last_login=timezone.now(),
            # )
            user = None

        return user

    def get_user(self, user_id):
        try:
            return MyUser(**requests.get(server_url + f"user/{user_id}").json())
        except Exception:
            # Djano Admin treats None user as anonymous your who have no right at all.
            return None
