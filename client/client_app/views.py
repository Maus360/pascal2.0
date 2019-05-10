from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy, reverse
from django.views import generic, View
from django.contrib import auth
from django.core.paginator import Paginator
from datetime import datetime

import logging
import requests
from .forms import MyUserCreationForm, BlogUpdateForm
from .models import Blog, Author

logger = logging.getLogger("pascal")


class LogInView(View):
    success_url = reverse_lazy("index")
    template_name = "registration/login.html"
    form_class = AuthenticationForm

    def get_context_data(self, **kwargs):
        context = kwargs
        # Get the blogger object from the "pk" URL parameter and add it to the context
        context["user"] = self.request.user
        return context

    def post(self, request, *args, **kwargs):

        # here you get the post request username and password
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        logger.info(
            "get username %s; password %s via post from user %s",
            username,
            password,
            request.user,
        )

        # authentication of the user, to check if it's active or None
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                # this is where the user login actually happens, before this the user
                # is not logged in.
                logger.info("authentificate user %s", user)
                auth.login(request, user)
                logger.info("user %s login", user)
                return HttpResponseRedirect(reverse("index"))
        else:
            logger.info("can't authentificate user")
            return render(
                request,
                self.template_name,
                {"form": self.form_class(request.POST), "user": request.user},
            )

    def get(self, request, *args, **kwargs):
        logger.info("get login page for user %s", request.user)
        return render(
            request,
            self.template_name,
            {"form": self.form_class(request.POST), "user": request.user},
        )


class LogOutView(View):
    success_url = reverse_lazy("index")
    template_name = "registration/logged_out.html"

    def get(self, request, *args, **kwargs):
        logger.info("user %s logout", request.user)
        auth.logout(request)
        return HttpResponseRedirect(self.success_url)


def index(request):
    logger.info("get index page")
    return render(request, "index.html")


class SignUpView(generic.CreateView):
    form_class = MyUserCreationForm
    success_url = reverse_lazy("index")
    template_name = "registration/signup.html"

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            logger.info("sign up with username %s; password %s", username, raw_password)
            user = auth.authenticate(username=username, password=raw_password)
            logger.info("authentificate user %s ", user)
            auth.login(request, user)
            logger.info("user %s login", user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request, self.template_name, {"form": self.form_class(request.POST)}
            )


class BlogListView(generic.ListView):
    model = Blog
    paginate_by = 5
    template_name = "client_app/blog_list.html"

    def get_context_data(self):
        context = dict()
        # Get the blogger object from the "pk" URL parameter and add it to the context
        blogs = Blog.objects.get_queryset()
        paginator = Paginator(blogs, self.paginate_by)
        page = self.request.GET.get("page")
        context["blog_list"] = context["page_obj"] = paginator.get_page(page)
        context["is_paginated"] = True
        # context["page_obj"] = paginator.get_page(page)
        return context


class BlogDeleteView(generic.DeleteView):
    model = Blog
    success_url = reverse_lazy("blogs")
    template_name = "client_app/blog_confirm_delete.html"

    def get_queryset(self):
        id_ = self.kwargs["pk"]
        self.queryset = Blog.objects.get(pk=id_)
        return self.queryset

    def get_context_data(self, **kwargs):
        context = dict()
        context["object"] = self.get_queryset()
        return context

    def get(self, request, *args, **kwargs):
        blog = self.get_queryset()
        logger.info(
            "user %s try to delete blog %s by author %s",
            request.user,
            blog,
            blog.author,
        )
        if request.user == blog.author.user:
            return render(request, self.template_name, context=self.get_context_data())
        else:
            return HttpResponseRedirect(
                reverse("blog-detail", kwargs={"pk": self.kwargs["pk"]})
            )

    def post(self, request, *args, **kwargs):
        self.items_to_delete = self.request.POST.getlist("itemsToDelete")
        if self.request.POST.get("confirm"):
            # when confirmation page has been displayed and confirm button pressed
            queryset = self.get_queryset()
            queryset.delete()  # deleting on the queryset is more efficient than on the model object
            logger.info(
                "user %s delete blog %s by author %s",
                request.user,
                queryset,
                queryset.author,
            )
            return HttpResponseRedirect(self.success_url)
        elif self.request.POST.get("cancel"):
            logger.info(
                "user %s not delete blog %s by author %s",
                request.user,
                self.get_queryset(),
                self.get_queryset().author,
            )
            # when confirmation page has been displayed and cancel button pressed
            return HttpResponseRedirect(self.success_url)
        else:
            # when data is coming from the form which lists all items
            return self.get(self, *args, **kwargs)


class BlogUpdateView(generic.UpdateView):
    model = Blog
    # fields = ["name", "description"]
    success_url = reverse_lazy("blogs")
    form_class = BlogUpdateForm
    template_name = "client_app/blog_form.html"

    def get_queryset(self):
        id_ = self.kwargs["pk"]
        self.queryset = Blog.objects.get(pk=id_)
        return self.queryset

    def get_object(self):
        id_ = self.kwargs["pk"]
        self.queryset = Blog.objects.get(pk=id_)
        return self.queryset

    def get_context_data(self, **kwargs):
        context = kwargs
        context["blog"] = self.get_queryset()
        context["form"] = self.form_class(instance=context["blog"])
        return context

    def get(self, request, *args, **kwargs):
        blog = self.get_queryset()
        logger.info(
            "user %s try to update blog %s by author %s",
            request.user,
            blog,
            blog.author,
        )
        if request.user == blog.author.user:
            return super(BlogUpdateView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(
                reverse("blog-detail", kwargs={"pk": self.kwargs["pk"]})
            )

    def form_valid(self, form):
        form.instance.post_date = datetime.today()
        return super().form_valid(form)


class BlogCreateView(generic.CreateView):
    model = Blog
    fields = ["name", "description"]
    success_url = reverse_lazy("blogs")
    template_name = "client_app/blog_form_create.html"

    def get_success_url(self):
        return reverse("blogs")

    def form_valid(self, form):
        user = self.request.user
        target_author = list(
            filter(lambda author: author.user == user, Author.objects.get_queryset())
        )
        if target_author == []:
            logger.info("register new author by user %s", self.request.user)
            form.instance.author = Author.objects.create(
                user=self.request.user, bio=f"I'am {self.request.user}"
            )
        else:

            form.instance.author = target_author[0]
        logger.info("user (%s) create blog (%s)", self.request.user, form.instance.name)
        form.instance.post_date = datetime.now()
        return super().form_valid(form)


class BlogDetailView(View):
    template_name = "client_app/blog_detail.html"

    def get_queryset(self):
        pk = self.kwargs["pk"]
        blog = Blog.objects.get(pk=pk)
        return blog

    def get_context_data(self):
        context = dict()
        # Get the blogger object from the "pk" URL parameter and add it to the context
        context["blog"] = self.get_queryset()
        return context

    def get(self, request, *args, **kwargs):
        logger.info(
            "user %s view blog %s by author %s",
            request.user,
            self.get_queryset(),
            self.get_queryset().author,
        )
        return render(request, self.template_name, context=self.get_context_data())


class BlogListbyAuthorView(generic.ListView):
    model = Blog
    paginate_by = 5
    template_name = "client_app/blog_list_by_author.html"

    def get_context_data(self):
        context = dict()
        id = self.kwargs["pk"]
        # Get the blogger object from the "pk" URL parameter and add it to the context
        context["blogger"] = Author.objects.get(pk=self.kwargs["pk"])
        blogs = list(
            filter(
                lambda blog: blog.author == context["blogger"],
                Blog.objects.get_queryset(),
            )
        )
        paginator = Paginator(blogs, self.paginate_by)
        page = self.request.GET.get("page")
        context["blog_list"] = context["page_obj"] = paginator.get_page(page)
        context["is_paginated"] = True

        return context


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 5
    template_name = "client_app/author_list.html"

    def get_context_data(self):
        context = dict()
        # Get the blogger object from the "pk" URL parameter and add it to the context
        authors = Author.objects.get_queryset()
        paginator = Paginator(authors, self.paginate_by)
        page = self.request.GET.get("page")
        context["author_list"] = context["page_obj"] = paginator.get_page(page)
        context["is_paginated"] = True
        return context
