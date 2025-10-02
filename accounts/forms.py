from django import forms
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class RegistrationForm(UserCreationForm):
    """The form a user register as a new user"""
    email = forms.EmailField(required=True, help_text='Enter a valid email address.')
    bio = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 60, 'placeholder': 'Tell us a bit about yourself...'}), 
        label="Bio (optional)", )
    photo = forms.ImageField(required=False, label="Profile photo (optional)")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'bio', 'photo']
    
    def save(self, commit=True):
        user = super().save(commit)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # save profile extras
            profile = user.profile
            profile.bio = self.cleaned_data.get('bio', '')
            profile.photo = self.cleaned_data.get('photo')
            profile.save()
        return user


class UserProfileForm(forms.ModelForm):
    """For editing user profile"""
    username = forms.CharField(max_length=150, 
    help_text="Required. 150 characters or fewer . Letters, digits and @/./+/-/_ only.",
)
    class Meta:
        model = Profile
        fields = ['username', 'bio', 'photo']
        widgets = {'bio': forms.Textarea(attrs={'rows':3, 'cols':60}),}
    
    def __init__(self, *args, **kwargs):
        # Expect an extra kwarg `instance` where instance.user is the User
        profile  = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        self.fields['username'].initial = profile.user.username
    
    def clean_username(self):
        """Check uniqueness of username"""
        username = self.cleaned_data['username']
        qs = User.objects.filter(username=username)
        # If there's any other user with the username, reject
        if qs.exists() and qs.first() != self.instance.user:
            raise forms.ValidationError("That username is already taken.")
        return username
    
    def save(self, commit=True):
        """Saves back to User and Profile"""
        profile = super().save(commit=False)
        profile.user.username = self.cleaned_data['username']
        if commit:
            profile.user.save()
            profile.save()
        return profile

class ConfirmPasswordForm(forms.Form):
    """"Confirm user's current password to change a new password."""
    password = forms.CharField(
        label="Current password", 
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

class EmailChangeForm(forms.ModelForm):
    """For changing user email"""
    class Meta:
        model = User
        fields = ['email']
        widgets = {'email': forms.EmailInput(attrs={'placeholder': 'new@example.com'})}

        def clean_email(self):
            """Check uniquness of email"""
            email = self.cleaned_data['email']
            qs = User.objects.exclude(pk=self.instance.pk).filter(email__iexact=email)
            if qs.exists():
                raise forms.ValidationError("That email is already in use.")
            return email
        
class ThemeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['theme']
        widgets = {'theme' : forms.RadioSelect(choices=Profile.THEME_CHOICES)}
