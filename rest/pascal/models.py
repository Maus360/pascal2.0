from datetime import datetime
from django.db import models

from django.urls import reverse
from django.contrib.auth.models import User


class Author(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    bio = models.TextField(max_length=400, help_text="Enter your bio details here")

    def get_absolute_url(self):
        """
        Returns the url to access a particular blog-author instance.
        """
        return reverse("author-detail", args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.user.username


class Blog(models.Model):
    """
    Model representing a blog post.
    """

    name = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    # Foreign Key used because Blog can only have one author/User, but bloggsers can have multiple blog posts.
    description = models.TextField(
        max_length=2000, help_text="Enter you blog text here."
    )
    post_date = models.DateTimeField(default=datetime.today)

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
