from django.shortcuts import render

# Create your views here.

from rest_framework import generics
from rest_framework import permissions
from .models import Post, Preference, Profile
from .serializers import TokenSerializer, UserSerializer, PostSerializer, PreferenceSerializer, ProfileSerializer
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.generic.base import RedirectView
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import F
from django.db import IntegrityError
import clearbit
from pyhunter import PyHunter

# Get the JWT settings
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

EMAILHUNTER_API_KEY = 'db2f5fd7957e5d03ac838c139c13e2f375fcace5'
CLEARBIT_API_KEY = 'sk_f9ad58528fd442b6d573632b50b20eb0'

LIKE = 1
UNLIKE = 0

class LoginView(generics.CreateAPIView):
    """
    POST auth/login/
    """
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "")
        password = request.data.get("password", "")

        if not username and not password:
            return Response(data={"message": "username and password is required to login a user"}, status=status.HTTP_400_BAD_REQUEST)
        elif not username:
            return Response(data={"message": "username is required to login a user"}, status=status.HTTP_400_BAD_REQUEST)
        elif not password:
            return Response(data={"message": "password is required to login a user"}, status=status.HTTP_400_BAD_REQUEST)
            
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                login(request, user)
                serializer = TokenSerializer(data={"token": JWT_ENCODE_HANDLER(JWT_PAYLOAD_HANDLER(user))})
                serializer.is_valid()
                return Response(serializer.data)
            except Exception as e:
                return Response(data={"message": e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data={"message": "can not authenticate with the given credentials or account is closed"}, status=status.HTTP_401_UNAUTHORIZED)


class RegisterUsers(generics.CreateAPIView):
    """
    POST auth/register/
    """
    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        email = request.data.get("email", "")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")

        if not username and not password and not email:
            return Response(data={"message": "username, password and email is required to register a user"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError as e:
            return Response(data={"message": "please provide proper email address"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hunter = PyHunter(EMAILHUNTER_API_KEY)
            email_verifier = hunter.email_verifier(email)
            if(not email_verifier or email_verifier['result'] == 'undeliverable'):
                return Response(data={"message": "email address: {} is not deliverable".format(email)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={"message": e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            new_user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        except IntegrityError as e:
            if 'UNIQUE constraint' in e.args[0]:
                return Response(data={"message": "username {} already exists".format(username)}, status=status.HTTP_409_CONFLICT)

        try:
            clearbit.key = CLEARBIT_API_KEY
            profile_data_clearbit = clearbit.Enrichment.find(email=email, stream=True)
        except Exception as e:
            return Response(data={"message": e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if profile_data_clearbit and 'person' in profile_data_clearbit:
            new_user.profile.bio = profile_data_clearbit['person']['bio']
            new_user.profile.site = profile_data_clearbit['person']['site']
            new_user.profile.location = profile_data_clearbit['person']['location']
            new_user.profile.timezone = profile_data_clearbit['person']['timeZone']
            new_user.profile.utc_offset = profile_data_clearbit['person']['utcOffset']
            new_user.profile.company_name = profile_data_clearbit['person']['employment']['name']
            new_user.profile.company_role = profile_data_clearbit['person']['employment']['role']
            new_user.profile.facebook_handle = profile_data_clearbit['person']['facebook']['handle']
            new_user.profile.twitter_handle = profile_data_clearbit['person']['twitter']['handle']
            new_user.profile.github_handle = profile_data_clearbit['person']['github']['handle']
            new_user.profile.linkedin_handle = profile_data_clearbit['person']['linkedin']['handle']
            new_user.profile.googleplus_handle = profile_data_clearbit['person']['googleplus']['handle']
            new_user.save()

        return Response(data=UserSerializer(new_user).data, status=status.HTTP_201_CREATED)


class LogoutView(RedirectView):
    """
    Logs out user and redirect to login url
    """
    query_string = True
    pattern_name = 'auth-login'

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(self.request)
        return super(LogoutView, self).get_redirect_url(*args, **kwargs)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET user/<user_id>/
    PUT user/<user_id>/
    DELETE user/<user_id>/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        try:
            user_obj = self.queryset.get(id=kwargs["user_id"])
            return Response(UserSerializer(user_obj).data)
        except User.DoesNotExist:
            return Response(data={"message": "user with user id: {} does not exist".format(kwargs["user_id"])}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        try:
            user_obj = self.queryset.get(id=kwargs["user_id"])
            first_name = request.data.get("first_name", "")
            last_name = request.data.get("last_name", "")
            email = request.data.get("email", "")
            username = request.data.get("username", "")
            location = request.data.get("location", "")
            bio = request.data.get("bio", "")
            site = request.data.get("site", "")

            if not request.user.is_authenticated:
                return Response(data={"message": "user is not logged in to update the user info"}, status=status.HTTP_401_UNAUTHORIZED)
            if request.user.username != user_obj.username:
                return Response(data={"message": "user is not authorized to update other user info"}, status=status.HTTP_401_UNAUTHORIZED)
            
            if not first_name and not last_name and not email and not username and not location and not bio and not site \
                    and not timezone and not utc_offset and not company_name and not company_role and not facebook_handle \
                    and not twitter_handle and not github_handle and not linkedin_handle and not googleplus_handle:
                return Response(data={"message": "no user info to update"}, status=status.HTTP_400_BAD_REQUEST)

            if email:
                return Response(data={"message": "cannot update email"}, status=status.HTTP_400_BAD_REQUEST)
            if username:
                if self.queryset.filter(username=username).exists():
                    return Response(data={"message": "username already taken"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    user_obj.username = username
            if first_name:
                user_obj.first_name = first_name
            if last_name:
                user_obj.last_name = last_name
            if location:
                user_obj.profile.location = location
            if bio:
                user_obj.profile.bio = bio
            if site:
                user_obj.profile.site = site
            if timezone:
                user_obj.profile.timezone = timezone
            if utc_offset:
                user_obj.profile.utc_offset = utc_offset
            if company_name:
                user_obj.profile.company_name = company_name
            if company_role:
                user_obj.profile.company_role = company_role
            if facebook_handle:
                user_obj.profile.facebook_handle = facebook_handle
            if twitter_handle:
                user_obj.profile.twitter_handle = twitter_handle
            if github_handle:
                user_obj.profile.github_handle = github_handle
            if linkedin_handle:
                user_obj.profile.linkedin_handle = linkedin_handle
            if googleplus_handle:
                user_obj.profile.googleplus_handle = googleplus_handle

            user_obj.save()
            return Response(UserSerializer(user_obj).data)
            
        except User.DoesNotExist:
            return Response(data={"message": "user with user id: {} does not exist".format(kwargs["user_id"])}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, *args, **kwargs):
        try:
            user_obj = self.queryset.get(id=kwargs["user_id"])

            if not request.user.is_authenticated:
                return Response(data={"message": "user is not logged in to delete the user info"}, status=status.HTTP_401_UNAUTHORIZED)
            if request.user.username != user_obj.username:
                return Response(data={"message": "user is not authorized to delete other user info"}, status=status.HTTP_401_UNAUTHORIZED)

            username = user_obj.username
            user_obj.delete()
            return Response(data={"message": "user {} has been deleted".format(username)}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(data={"message": "user with user id: {} does not exist".format(kwargs["user_id"])}, status=status.HTTP_404_NOT_FOUND)


class ListUsersView(generics.ListAPIView):
    """
    GET user/all/
    """
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer


class ListPostsView(generics.ListAPIView):
    """
    GET post/all/
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class ListPostsByUserView(generics.ListAPIView):
    """
    GET post/all/<username>/
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    def get(self, request, *args, **kwargs):
        username = kwargs["username"]
        try:
            user_obj = User.objects.get(username=username)
            posts_by_user = self.queryset.filter(author=user_obj)
            return Response(self.serializer_class(posts_by_user, many=True).data)
        except User.DoesNotExist:
            return Response(data={"message": "user with username: {} does not exist".format(username)}, status=status.HTTP_404_NOT_FOUND)


class CreatePostView(generics.CreateAPIView):
    """
    POST post/
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def post(self, request, *args, **kwargs):
        content = request.data.get("content", "")
        author = request.user
        
        if not content:
            return Response(data={"message": "post is empty"}, status=status.HTTP_400_BAD_REQUEST)

        post_obj = Post.objects.create(content=content, likes=0, unlikes=0, author=author)
        return Response(data=PostSerializer(post_obj).data, status=status.HTTP_201_CREATED)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET post/<int:post_id>/
    PUT post/<int:post_id>/
    DELETE post/<int:post_id>/
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get(self, request, *args, **kwargs):
        post_id = kwargs["post_id"]

        try:
            post_obj = self.queryset.get(id=post_id)
            return Response(data=self.serializer_class(post_obj).data)
        except Post.DoesNotExist:
            return Response(data={"message": "post with post_id: {} does not exist".format(post_id)}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        post_id = kwargs["post_id"]
        content = request.data.get("content", "")

        if not request.user.is_authenticated:
            return Response(data={"message": "user is not logged in to update the post"}, status=status.HTTP_401_UNAUTHORIZED)

        if not content:
            return Response(data={"message":"post is empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            post_obj = self.queryset.get(id=post_id)
            if request.user.username != post_obj.author.username:
                return Response(data={"message": "user is not authorized to update the post by other user"}, status=status.HTTP_401_UNAUTHORIZED)
            
            post_obj.content = content
            post_obj.save()
            return Response(data=self.serializer_class(post_obj).data)
        except Post.DoesNotExist:
            return Response(data={"message": "post with post_id: {} does not exist".format(post_id)}, status=status.HTTP_404_NOT_FOUND)
        
    def delete(self, request, *args, **kwargs):
        post_id = kwargs["post_id"]

        if not request.user.is_authenticated:
            return Response(data={"message": "user is not logged in to delete the post"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            post_obj = self.queryset.get(id=post_id)

            if request.user.username != post_obj.author.username:
                return Response(data={"message": "user is not authorized to delete the post by other user"}, status=status.HTTP_401_UNAUTHORIZED)

            post_obj.delete()
            return Response(data={"message": "post with post_id: {} deleted".format(post_id)}, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response(data={"message": "post with post_id: {} does not exist".format(post_id)}, status=status.HTTP_404_NOT_FOUND)


class ListPreferencesView(generics.ListAPIView):
    """
    GET preference/all/
    """
    queryset = Preference.objects.all()
    serializer_class = PreferenceSerializer


class PreferenceDetailView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    """
    GET preference/<int:post_id>/ 
    POST reference/<int:post_id>/
    PUT preference/<int:post_id>/
    DELETE preference/<int:post_id>/
    """
    queryset = Preference.objects.all()
    serializer_class = PreferenceSerializer

    def get(self, request, *args, **kwargs):
        post_id = kwargs["post_id"]

        try:
            post_obj = Post.objects.get(id=post_id)

            if not self.queryset.filter(post=post_obj).exists():
                return Response(data={"message": "no preference exists for post id: {}".format(post_id)}, status=status.HTTP_404_NOT_FOUND)

            pref_objs = self.queryset.filter(post=post_obj)
            return Response(self.serializer_class(pref_objs).data, many=True)
        except Post.DoesNotExist:
            return Response(data={"message": "post with post_id: {} does not exist".format(post_id)}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        post_id = kwargs["post_id"]
        pref_value = int(request.data.get("pref_value", "-1"))
        user = request.user

        if not user.is_authenticated:
            return Response(data={"message": "user is not logged in to fill the preference"}, status=status.HTTP_401_UNAUTHORIZED)

        if pref_value == -1:
            return Response(data={"message": "preference value not provided"}, status=status.HTTP_400_BAD_REQUEST)

        if pref_value != LIKE and pref_value != UNLIKE:
            return Response(data={"message": "invalid value of preference. Please provide {} for like or {} for unlike.".format(LIKE, UNLIKE)},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            post_obj = Post.objects.get(id=post_id)

            if not Preference.objects.filter(post=post_obj, user=user).exists():
                if post_obj.author.username == user.username:
                    return Response(data={"message": "user can't fill preference of his own post"}, status=status.HTTP_400_BAD_REQUEST)

                pref_obj = Preference.objects.create(post=post_obj, user=user, value=pref_value)
                if pref_value == LIKE:
                    post_obj.likes = F('likes') + 1
                else:
                    post_obj.unlikes = F('unlikes') + 1
                post_obj.save()
                post_obj.refresh_from_db()

                return Response(self.serializer_class(pref_obj).data, status=status.HTTP_201_CREATED)
            else:
                return Response(data={"message": "preference for this post already exists by the user. Please use PUT to update."}, status=status.HTTP_400_BAD_REQUEST)

        except Post.DoesNotExist:
            return Response(data={"message": "post with post_id: {} does not exist".format(post_id)}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        post_id = kwargs["post_id"]
        pref_value = int(request.data.get("pref_value", "-1"))
        user = request.user

        if not user.is_authenticated:
            return Response(data={"message": "user is not logged in to update the preference"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            post_obj = Post.objects.get(id=post_id)

            if not self.queryset.filter(post=post_obj, user=user).exists():
                return Response(data={"message":"no preference exists for post id: {}".format(post_id)}, status=status.HTTP_404_NOT_FOUND)

            if pref_value == -1:
                return Response(data={"message":"preference value not provided"}, status=status.HTTP_400_BAD_REQUEST)

            if pref_value != LIKE and pref_value != UNLIKE:
                return Response(data={"message":"invalid value of preference. Please provide {} for like or {} for unlike.".format(LIKE, UNLIKE)},
                                 status=status.HTTP_400_BAD_REQUEST)

            pref_obj = self.queryset.filter(post=post_obj, user=user).get()
            old_pref_value = pref_obj.value
            new_pref_value = pref_value
            if old_pref_value == new_pref_value:
                action = None
                if new_pref_value == LIKE:
                    action = "like"
                else:
                    action = "unlike"
                return Response(data={"message": "user can't {} this post more than once".format(action)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                pref_obj.value = new_pref_value
                pref_obj.save()
                if new_pref_value == LIKE:
                    post_obj.likes = F('likes') + 1
                    post_obj.unlikes = F('unlikes') - 1
                else:
                    post_obj.likes = F('likes') - 1
                    post_obj.unlikes = F('unlikes') + 1
                
                post_obj.save()
                post_obj.refresh_from_db()
                return Response(self.serializer_class(pref_obj).data)
        except Post.DoesNotExist:
            return Response(data={"message": "post with post_id: {} does not exist".format(post_id)}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        post_id = kwargs["post_id"]
        user = request.user

        if not user.is_authenticated:
            return Response(data={"message": "user is not logged in to delete preference"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            post_obj = Post.objects.get(id=post_id)

            if not self.queryset.filter(post=post_obj, user=user).exists():
                return Response(data={"message": "no preference exists for post id: {}".format(post_id)}, status=status.HTTP_404_NOT_FOUND)

            pref_obj = self.queryset.filter(post=post_obj, user=user).get()
            pref_value = pref_obj.value
            pref_obj.delete()
            if pref_value == LIKE:
                post_obj.likes = F('likes') - 1
            else:
                post_obj.likes = F('unlikes') - 1
            post_obj.save()

            return Response(data={"message": "preference for post_id: {} deleted".format(post_id)}, status=status.HTTP_204_NO_CONTENT)
        
        except Post.DoesNotExist:
            return Response(data={"message": "post with post_id: {} does not exist".format(post_id)}, status=status.HTTP_404_NOT_FOUND)
        
