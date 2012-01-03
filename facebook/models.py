import json
import urllib

from django.db import models
from django.contrib.auth.models import User


class FacebookProfile(models.Model):
    user = models.OneToOneField(User, related_name='_facebook')
    facebook_id = models.BigIntegerField()
    access_token = models.CharField(max_length=150)

    def get_facebook_profile(self):
        fb_profile = urllib.urlopen(
                        'https://graph.facebook.com/me?access_token=%s'
                        % self.access_token)
        data = json.load(fb_profile)
        data.update({'picture': self.get_facebook_picture()})
        return data

    def get_facebook_picture(self):
        return u'http://graph.facebook.com/%s/picture?type=large' \
                                                            % self.facebook_id

    def save(self):
        # updates user avatar
        super(FacebookProfile, self).save()
        self.user.avatar = self.get_facebook_picture()
        self.user.save()
