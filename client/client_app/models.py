from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings

import logging
import requests
from datetime import datetime

logger = logging.getLogger("model")
server_url = settings.SERVER_URL


class MyUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        data = {"username": username, "password": password, "last_login": ""}
        user = MyUser(**data)
        return user

    def create_superuser(self, email, username, password, date_of_birth):
        user = self.create_user(password=password, username=username)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

    def get(self, pk):
        logger.info("select user %s", pk)
        return MyUser(**requests.get(pk).json())


class AuthorManager(models.Manager):
    def create(self, user, bio):
        data = {"user": server_url + f"user/{user.id}/", "bio": bio}
        logger.info("create author with data %s", data)
        author = requests.post(server_url + "author/", data=data)
        logger.info("response: %s, json: %s", author, author.json())
        author = author.json()
        author["user"] = MyUser.objects.get(author["user"])
        author = Author(**author)
        return author

    def get_queryset(self):
        logger.info("select all author")
        authors = requests.get(server_url + "author/")
        logger.info("response: %s, json: %s", authors, authors.json())
        authors = authors.json()
        for author in authors:
            author["user"] = MyUser(**requests.get(author["user"]).json())
        return [Author(**author) for author in authors]

    def get(self, pk):
        if isinstance(pk, int):
            logger.info("select author by id %i", pk)
            author = requests.get(server_url + f"author/{pk}")
        else:
            logger.info("select author %s", pk)
            author = requests.get(pk)
        logger.info("response: %s, json: %s", author, author.json())
        author = author.json()
        author["user"] = MyUser.objects.get(author["user"])
        return Author(**author)


class BlogManager(models.Manager):
    def create(self, name, author, description, post_date):
        data = {
            "name": name,
            "author": author.id,
            "description": description,
            "post_date": post_date,
        }
        logger.info("create blog with data %s", str(data))
        blog = requests.post(server_url + "blog/", data=data)
        blog = Blog(**blog.json())
        logger.info("response: %s, json: %s", blog, blog.json())
        return blog

    def get_queryset(self):
        logger.info("select all blog")
        blogs = requests.get(server_url + "blog/")
        logger.info("response: %s, json: %s", blogs, blogs.json())
        blogs = blogs.json()
        for blog in blogs:
            blog["author"] = Author.objects.get(blog["author"])
            blog["post_date"] = datetime.strptime(
                blog["post_date"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            blog["post_date"] = datetime.strftime(blog["post_date"], "%d-%m-%Y %H:%M")
        blogs = [Blog(**blog) for blog in blogs]
        return blogs

    def get(self, pk):
        if isinstance(pk, int):
            logger.info("select blog by id %i", pk)
            blog = requests.get(server_url + f"blog/{pk}")
        else:
            logger.info("select blog %s", pk)
            blog = requests.get(pk)
        logger.info("response: %s, json: %s", blog, blog.json())
        blog = blog.json()
        blog["author"] = Author.objects.get(blog["author"])
        blog["post_date"] = datetime.strptime(
            blog["post_date"], "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        blog["post_date"] = datetime.strftime(blog["post_date"], "%d-%m-%Y %H:%M")
        return Blog(**blog)


class MyUser(AbstractUser):
    objects = MyUserManager()

    def save(self, *args, **kwargs):
        save_data = {"username": "", "password": "", "last_login": ""}
        for field in save_data.keys():
            save_data[field] = self.__getattribute__(field)
        logger.info("save user with data %s", str(save_data))
        result = requests.put(server_url + f"user/{self.id}/", data=save_data)
        logger.info("response: %s, json: %s", result, result.json())
        if result.json().get("detail", None) == "Not found.":
            logger.info("create user with data %s", str(save_data))
            result = requests.post(server_url + f"user/", data=save_data)
            logger.info("response: %s, json: %s", result, result.json())


class Author(models.Model):
    objects = AuthorManager()
    user = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True)
    bio = models.TextField(max_length=400, help_text="Enter your bio details here")

    class Meta:
        ordering = ["user", "bio"]

    def get_absolute_url(self):
        """
        Returns the url to access a particular blog-author instance.
        """
        return reverse("blogs-by-author", args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object.
        """
        return str(self.user.username)

    def save(self, *args, **kwargs):
        save_data = {"user": "", "bio": ""}
        for field in save_data.keys():
            save_data[field] = self.__getattribute__(field)
        logger.info("save author with data %s", str(save_data))
        result = requests.put(server_url + f"author/{self.id}/", data=save_data)
        logger.info("response: %s, json: %s", result, result.json())


class Blog(models.Model):
    """
    Model representing a blog post.
    """

    objects = BlogManager()
    name = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    # Foreign Key used because Blog can only have one author/User, but bloggsers can have multiple blog posts.
    description = models.TextField(
        max_length=2000, help_text="Enter you blog text here."
    )
    post_date = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ["-post_date"]

    def get_absolute_url(self):
        """
        Returns the url to access a particular blog instance.
        """
        return reverse("blog-detail", args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object.
        """

        return self.name

    def save(self, *args, **kwargs):
        save_data = {"name": "", "author": "", "description": "", "post_date": ""}
        for field in save_data.keys():
            save_data[field] = self.__getattribute__(field)
        logger.info("save blog with data %s", str(save_data))
        save_data["author"] = server_url + f"author/{save_data['author'].id}/"
        result = requests.put(server_url + f"blog/{self.id}/", data=save_data)
        logger.info("response: %s, json: %s", result, result.json())
        if result.json().get("detail", None) == "Not found.":
            logger.info("create blog with data %s", str(save_data))
            result = requests.post(server_url + f"blog/", data=save_data)
            logger.info("response: %s, json: %s", result, result.json())

    def delete(self):
        logger.info("delete blog by id %i", self.id)
        result = requests.delete(server_url + f"blog/{self.id}/")


# Create your models here.
