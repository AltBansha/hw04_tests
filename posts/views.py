from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    post_list = Post.objects.select_related("group")
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request,
                  "index.html",
                  {"page": page,
                   "post_list": post_list,
                   "paginator": paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 12)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "group.html", {
            "page": page,
            "group": group,
            "posts": posts,
            "paginator": paginator,
        }
    )


def group_list(request):
    groups = Group.objects.all()
    return render(request, "posts/group_list.html", {"groups": groups})


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if request.method == 'GET' or not form.is_valid():
        return render(request, "posts/new.html", {"form": form})
    
    post = form.save(commit=False)
    post.author = request.user
    form.save()
    return redirect("index")


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    post_count = post_list.count()
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {"page": page,
               "author": author,
               "post_count": post_count,
               "paginator": paginator}
    return render(request, "posts/profile.html", context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post,id=post_id, author__username=username)
    count = Post.objects.count()
    context = {"post": post,
               "author": post.author,
               "count": count}
    return render(request, "posts/post.html", context)


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user != post.author:
        return redirect("post", username=username, post_id=post_id)

    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        post = form.save()
        return redirect("post",
                        username=username,
                        post_id=post_id)

    return render(request, "posts/new.html", {"form": form,
                                              "post": post,
                                              "is_edit": True})
