from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.urls import reverse
from .variables import posts_per_page
from typing import Dict
from .models import Post, Country, User, Follow, Like
from .forms import PostForm, CommentForm


def index(request: HttpRequest) -> HttpResponse:
    posts = Post.objects\
        .select_related('author')\
        .select_related('country')\
        .all()

    paginator = Paginator(posts, posts_per_page)
    page_number = request.GET.get('page')
    page_posts = paginator.get_page(page_number)

    context = {
        'page_posts': page_posts,
    }
    template = 'posts/index.html'

    return render(request, template, context)


@login_required(login_url='users:login')
def follow_index(request: HttpRequest) -> HttpResponse:
    posts = Post.objects.filter(author__following__user=request.user)

    paginator = Paginator(posts, posts_per_page)
    page_number = request.GET.get('page')
    page_posts = paginator.get_page(page_number)

    context = {'page_posts': page_posts, }

    return render(request, 'posts/follow.html', context)


def country_posts(request: HttpRequest, slug: str) -> HttpResponse:
    country = get_object_or_404(Country, slug=slug)
    posts = country.posts.all()
    paginator = Paginator(posts, posts_per_page)
    page_number = request.GET.get('page')
    page_posts = paginator.get_page(page_number)

    context: Dict[str, str] = {
        'country': country,
        'page_posts': page_posts,
    }
    templates = 'posts/country_posts.html'

    return render(request, templates, context)


def profile(request: HttpRequest, user_name: str) -> HttpResponse:
    user = get_object_or_404(User, username=user_name)
    posts = Post.objects.filter(author=user)

    paginator = Paginator(posts, posts_per_page)
    page_number = request.GET.get('page')
    page_posts = paginator.get_page(page_number)

    follow_list = Follow.objects.all()
    following = False
    if request.user.is_authenticated:
        following = follow_list.filter(user=request.user, author=user).exists()
    followers_count = follow_list.filter(author=user).count()
    following_count = follow_list.filter(user=user).count()

    context = {
        'page_posts': page_posts,
        'author': user,
        'posts': posts,
        'following': following,
        'followers_count': followers_count,
        'following_count': following_count,
    }

    templates = 'posts/profile.html'

    return render(request, templates, context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()

    form = CommentForm(request.POST or None)

    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }

    templates = 'posts/post_detail.html'

    return render(request, templates, context)


@login_required(login_url='users:login')
def post_create(request: HttpRequest) -> HttpResponse:
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()

        return redirect('travel_posts:profile', request.user)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required(login_url='users:login')
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect('travel_posts:main')

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()

        return redirect('travel_posts:post_detail', post_id)

    return render(
        request,
        'posts/update_post.html',
        {'form': form, 'post': post}
    )


@login_required(login_url='users:login')
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, id=post_id)

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('travel_posts:post_detail', post_id)


@login_required(login_url='users:login')
def profile_follow(request: HttpRequest, user_name: str) -> HttpResponse:
    author = get_object_or_404(User, username=user_name)

    already_follow = Follow.objects.filter(user=request.user, author=author)
    if request.user != author and not already_follow:
        Follow.objects.create(user=request.user, author=author)

    return redirect('travel_posts:profile', user_name)


@login_required(login_url='users:login')
def profile_unfollow(request: HttpRequest, user_name: str) -> HttpResponse:
    author = get_object_or_404(User, username=user_name)
    Follow.objects.filter(user=request.user, author=author).delete()

    return redirect('travel_posts:profile', user_name)


@login_required(login_url='users:login')
def post_like(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)

    already_like = Like.objects.filter(user=request.user, post=post)
    if not already_like:
        Like.objects.create(user=request.user, post=post)

    return HttpResponseRedirect(
        request.META.get('HTTP_REFERER'),
        reverse('travel_posts:post_detail', kwargs={'post_id': post_id})
    )


@login_required(login_url='users:login')
def post_dislike(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)
    Like.objects.filter(user=request.user, post=post).delete()

    return HttpResponseRedirect(
        request.META.get('HTTP_REFERER'),
        reverse('travel_posts:post_detail', kwargs={'post_id': post_id})
    )
