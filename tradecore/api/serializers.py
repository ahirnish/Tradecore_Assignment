from rest_framework import serializers
from .models import Profile, Post, Preference
from django.contrib.auth.models import User

class TokenSerializer(serializers.Serializer):
    """
    Serializer for JWT token.
    """
    token = serializers.CharField(max_length=255)


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile having additional information of user. 
    """
    class Meta:
        model = Profile
        fields = ("location", "bio", "site", "timezone", "utc_offset", "company_name",
                  "company_role", "facebook_handle", "twitter_handle", "github_handle",
                  "linkedin_handle", "googleplus_handle")
        depth = 2


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for base information of user.
    """
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "profile")


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for social media post authored by user.
    """
    author = UserSerializer()

    class Meta:
        model = Post
        fields = ("id", "content", "likes", "unlikes", "created_at", "updated_at", "author")
        depth = 2


class PreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for 'like' or 'unlike' information on a post by user.
    """
    user = UserSerializer()
    post = PostSerializer()

    class Meta:
        model = Preference
        fields = ("user", "post", "value", "created_at", "updated_at")
        depth = 2
