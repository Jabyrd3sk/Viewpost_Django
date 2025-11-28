from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import UserProfileForm, RegistrationForm, ConfirmPasswordForm, EmailChangeForm, ThemeForm
from viewpost.models import Post
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType

def register(request):
    """Register a new user, log them in, send them welcome email"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Send welcome email
            send_mail(
                'Welcome to Viewpost!', 
                f'Hi {user.username},\n\nThanks for signing up to ViewPost! Start sharing your moments.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False
            )
            # a "success" message when sucessfully registered
            messages.success(request, "You've Successfully registered! Please log in to continue")
            # login(request, user)
            
            # Don't auto login, send them to the login page
            return redirect('accounts:login')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def view_profile(request, username):
    """Show a user's profile, their posts, and follow counts."""
    # Look up the user profile
    user = get_object_or_404(Profile, user__username = username).user
    profile = user.profile
    # Get the user's posts and counts
    posts = Post.objects.filter(owner=user)
    posts_count = posts.count()
    # Get follow counts
    following_count = profile.following.count()
    followers_count = profile.followers.count()
    
    context = {
        'profile': profile,
        'posts': posts,
        'posts_count': posts_count,
        'following_count': following_count,
        'followers_count': followers_count,
    }
    return render(request, 'registration/profile.html', context)


@login_required
def edit_profile(request):
    """Edit username and profile photo"""
    profile = request.user.profile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            messages.error(request, "Something went wrong.")
            return redirect('accounts:profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'registration/edit_profile.html', {'form': form})


@login_required
def toggle_follow(request, username):
    """Follow or unfollow a user."""
    target_profile = get_object_or_404(Profile, user__username=username)
    me = request.user.profile

    if target_profile.user != request.user:
        if target_profile in me.following.all():
            me.following.remove(target_profile)
        else:
            me.following.add(target_profile)
            # Notify the user they've been followed
            Notification.objects.create(
                recipient=target_profile.user,
                actor=request.user,
                verb='started following you',
            )
    return redirect('accounts:profile', username=username)
    

@login_required
def followers_list(request, username):
    """Show users who follow <username>"""
    profile = get_object_or_404(Profile, user__username=username)
    # profile.followers is a queryset of Profile instances
    followers = profile.followers.all()
    return render(request, 'registration/followers_list.html', {'profile_owner': profile.user, 'profiles': followers,})

@login_required
def following_list(request, username):
    """Show users whom <username> is following."""
    profile = get_object_or_404(Profile, user__username=username)
    following = profile.following.all()
    return render(request, 'registration/following_list.html', {'profile_owner': profile.user, 'profiles': following,})

@login_required
def search_users(request):
    """Search users by username substring."""
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        # Case-insensitive partial match
        results = User.objects.filter(username__icontains=query)
    return render(request, 'registration/search_users.html', {'query': query, 'results': results,})

@login_required
def settings_page(request):
    """
    Show links to account actions: edit profile, change email, change password 
    and display log out and delete-account actions.
    """
    profile = request.user.profile
    profile_form = UserProfileForm(instance=profile)
    if request.method == 'POST':
        # Determine which form was submitted
        if 'update_profile' in request.POST:
            pass

        elif 'update_theme' in request.POST:
            theme_form = ThemeForm(request.POST, instance=profile)
            if theme_form.is_valid():
                theme_form.save()
                messages.success(request, "Theme updated.")
                return redirect('accounts:settings')
    else:
        theme_form = ThemeForm(instance=profile)
    
    return render(request, 'registration/settings.html', {'theme_form': theme_form})

@login_required
def delete_account(request):
    """Ask for the user's password, then delete if it matches"""
    if request.method == 'POST':
        form = ConfirmPasswordForm(request.POST)
        if form.is_valid():
            pwd = form.cleaned_data['password']
            # verify the password
            if request.user.check_password(pwd):
                # remove the user and log them out
                request.user.delete()
                return redirect('viewpost:index')
            else:
                form.add_error('password', 'Incorrect password.')
    else:
        form = ConfirmPasswordForm()
    return render(request, 'registration/confirm_delete_account.html', {'form': form})

@login_required
def change_email(request):
    """Let a user change their email address."""
    if request.method == 'POST':
        form = EmailChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your email has been updated.")
            return redirect('accounts:settings')
    else:
        form = EmailChangeForm(instance=request.user)
    return render(request, 'registration/change_email.html', {'form': form})





