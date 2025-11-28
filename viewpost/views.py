from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from . models import Post, Comment
from .forms import PostForm, CommentForm
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse

@login_required
def post_list(request):
    """
    Shows all posts EXCEPT the ones the current user made.
    User's own posts should only appear on their profile page.
    """
    # Exclude the logged-in user's posts
    posts = Post.objects.exclude(owner=request.user).order_by('-created_at')
    comment_form = CommentForm()
    context = {'posts': posts, 'comment_form': comment_form, }
    return render(request, 'viewpost/post_list.html', context)

# for anonymous visitors to see all public posts
# def post_list(request):
#     if request.user.is_authenticated:
#         posts = Post.objects.exclude(owner=request.user)
#     else:
#         posts = Post.objects.all()
#     posts = posts.order_by('-created_at')

@login_required
def new_post(request):
    """Create a new post."""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.owner = request.user
            post.save()
            return redirect('viewpost:post_list')
    else:
        form = PostForm()
    return render(request, 'viewpost/new_post.html', {'form': form})

@login_required
def delete_post(request, post_id):
    """Delete an existing post."""
    post = get_object_or_404(Post, id=post_id, owner=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('accounts:profile', username=request.user.username)
    return render(request, 'viewpost/confirm_delete.html', {'post': post})

@login_required
def like_post(request, post_id):
    """"Like an existing post."""
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True
        # Create a notification but don't notify urself
        if post.owner != user:
            Notification.objects.create(
                recipient=post.owner,
                actor=user,
                verb='liked your post',
                target_ct=ContentType.objects.get_for_model(Post),
                target_id=post.id
            )
    count = post.likes.count()
    # If this is an Ajax request, return JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'count': count})

    # Redirect back to whatever page you were on
    return redirect(request.META.get('HTTP_REFERER', 'viewpost:post_list'))

@login_required
def add_comment(request, post_id):
    """Add a Comment on existing post."""
    post = get_object_or_404(Post, id=post_id) 
    user = request.user
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = user
            comment.save()
            # Notify post owner (unless they commented on their on post)
            if post.owner != user:
                Notification.objects.create(
                    recipient=post.owner,
                    actor=user,
                    verb='commented on your post',
                    target_ct=ContentType.objects.get_for_model(Post),
                    target_id=post.id)
            return redirect(request.META.get('HTTP_REFERER', 'viewpost:post_list'))
            
    else:
        form = CommentForm()
    return render(request, 'viewpost/comment_page.html', {'post': post, 'form': form,})

@login_required
def delete_comment(request, comment_id):
    """Delete an existing comment."""
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    if request.method == 'POST':
        comment.delete()
    return redirect('viewpost:post_list')

@login_required
def comment_page(request, post_id):
    """Show a form to add a comment to post"""
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    top_comments = post.comments.filter(parent__isnull=True)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            # handling threading.........
            parent_id = form.cleaned_data.get('parent')
            if parent_id:
                comment.parent = Comment.objects.get(id=parent_id)
            comment.save()
            
            # Notify post owner, except if they commented on their on post
            if post.owner != user:
                Notification.objects.create(
                    recipient=post.owner,
                    actor=user,
                    verb='commented on your post',
                    target_ct=ContentType.objects.get_for_model(Post),
                    target_id=post.id)
            return redirect(request.META.get('HTTP_REFERER', 'viewpost:post_list'))
    else:
        form = CommentForm()
    top_comments = post.comments.filter(parent__isnull=True).order_by('date_added')
    return render(request, 'viewpost/comment_page.html', {'post': post, 'form': form, 'top_comments': top_comments})

@login_required
def following_feed(request):
    """Show posts posted by users that the current user follows."""
    # get the User objects you follow
    followees = request.user.profile.following.values_list('user', flat=True)
    posts = Post.objects.filter(owner__in=followees) \
                            .order_by('-created_at')
    return render(request, 'viewpost/following.html', {'posts': posts})

def index(request):
    return render(request, 'viewpost/index.html')
