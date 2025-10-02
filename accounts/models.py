from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio =  models.TextField(blank=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    # For dark or light mode
    THEME_CHOICES = [('light', 'Light'), ('dark', 'Dark')]
    theme = models.CharField(max_length=5, choices=THEME_CHOICES, default='light')
    
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
# Automatically create/update Profile when User is created:
@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, **kwargs):
    # Ensure a Profile exists for this user, then save it.
    profile, _ = Profile.objects.get_or_create(user=instance)
    profile.save()