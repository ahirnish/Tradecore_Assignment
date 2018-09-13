from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Profile( models.Model ):
    '''
    Model to hold additional detail of user.
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, blank=True, null=True, help_text="location of user")
    bio = models.CharField(max_length=255, blank=True, null=True, help_text="brief description about user")
    site = models.CharField(max_length=100, blank=True, null=True, help_text="website of user")
    timezone = models.CharField(max_length=100, blank=True, null=True, help_text="time zone of user")
    utc_offset = models.IntegerField(blank=True, null=True, help_text="difference in hours from UTC timezone")
    company_name = models.CharField(max_length=100, blank=True, null=True, help_text="name of the company of user")
    company_role = models.CharField(max_length=100, blank=True, null=True, help_text="role of user in the company")
    facebook_handle = models.CharField(max_length=100, blank=True, null=True, help_text="facebook handle of user")
    twitter_handle = models.CharField(max_length=100, blank=True, null=True, help_text="twitter handle of user")
    github_handle = models.CharField(max_length=100, blank=True, null=True, help_text="github handle of user")
    linkedin_handle = models.CharField(max_length=100, blank=True, null=True, help_text="linkedin handle of user")
    googleplus_handle = models.CharField(max_length=100, blank=True, null=True, help_text="googleplus handle of user")

    def __str__(self):
        return self.user.username + ', ' + self.location


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Post( models.Model ):
    """
    Model to hold detail of social media post authored by user.
    """
    content = models.CharField(max_length=255, null=False, help_text="content of the post")
    likes = models.IntegerField(default=0, null=False, help_text="number of likes")
    unlikes = models.IntegerField(default=0, null=False, help_text="number of unlikes")
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False, help_text="author of the post")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']


class Preference( models.Model ):
    """
    Model to hold detail of 'like' or 'unlike' on a post by user.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, help_text="post whose preference to be set")
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="user whose preference to be set")
    value = models.BooleanField(help_text="1 for like, 0 for unlike")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("post", "user")
        ordering = ['id']
