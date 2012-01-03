import cgi
import urllib
import json

from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.db import IntegrityError
from django.core.urlresolvers import reverse

from facebook.models import FacebookProfile


class FacebookBackend:
    def authenticate(self, token=None, request=None):
        """ Reads in a Facebook code and asks Facebook if it's valid and what
        user it points to. """
        args = {
            'client_id': settings.FACEBOOK_APP_ID,
            'client_secret': settings.FACEBOOK_APP_SECRET,
            'redirect_uri': request.build_absolute_uri(
                                            reverse('facebook-callback')),
            'code': token,
        }

        # Get a legit access token
        target = urllib.urlopen(
                        'https://graph.facebook.com/oauth/access_token?'
                            + urllib.urlencode(args)).read()
        response = cgi.parse_qs(target)
        access_token = response['access_token'][-1]

        # Read the user's profile information
        fb_profile = urllib.urlopen(
                'https://graph.facebook.com/me?access_token=%s' % access_token)
        fb_profile = json.load(fb_profile)

        try:
            # Try and find existing user
            fb_user = FacebookProfile.objects.get(facebook_id=fb_profile['id'])
            user = fb_user.user
            # Update access_token
            fb_user.access_token = access_token
            fb_user.save()
        except FacebookProfile.DoesNotExist:
            # See if email has already been registered
            try:
                user = User.objects.get(email=fb_profile['email'])
            except User.DoesNotExist:
                # No existing user, create one
                user = User.objects.create_user(fb_profile['id'],
                                                fb_profile['email'])
                user.first_name = fb_profile['first_name']
                user.last_name = fb_profile['last_name']
                # with django-primate User has one field called 'name' instead
                # of first_name and last_name
                user.name = u'%s %s' % (user.first_name, user.last_name)
                user.save()

            # Create the FacebookProfile
            fb_user = FacebookProfile(user=user,
                                      facebook_id=fb_profile['id'],
                                      access_token=access_token)
            fb_user.save()
        return user

    def get_user(self, user_id):
        """ Just returns the user of a given ID. """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    supports_object_permissions = False
    supports_anonymous_user = True
