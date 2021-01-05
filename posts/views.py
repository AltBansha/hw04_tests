from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    post_list = Post.objects.select_related("group").order_by("-pub_date")
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request,
                  "index.html",
                  {"page": page,
                   "paginator": paginator})
    # latest = Post.objects.order_by("-pub_date")[:10]
    # return render(request, "index.html", {"posts": latest})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all().order_by("-pub_date")
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
    # posts = group.posts.all().order_by("-pub_date")[:12]
    # return render(request, "group.html", {"group": group, "posts": posts})


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
    post_list = author.posts.all().order_by("-pub_date")
    post_count = post_list.count()
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "posts/profile.html", {"page": page,
                                                  "author": author,
                                                  "post_count": post_count,
                                                  "paginator": paginator})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    count = Post.objects.filter(author=author).select_related("author").count()
    return render(request, "posts/post.html", {"post": post,
                                               "author": author,
                                               "count": count})


def post_edit(request, username, post_id):
    author = User.objects.get(username=username)
    post = get_object_or_404(Post, author=author, id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect(
                "post",
                username=request.user.username,
                post_id=post.id
            )
    form = PostForm(instance=post)
    return render(
        request,
        "posts/new.html", {
            "form": form,
            "post": post,
            "is_edit": True,
        }
    )
