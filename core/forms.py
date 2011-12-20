from django import forms
from django.contrib.auth.models import User
from core.models import Category

from django.forms.widgets import CheckboxSelectMultiple

# httplib used to check that image url is a valid resource
import httplib
from urlparse import urlparse


class SubmissionForm(forms.Form):
    # TODO this needs to be dynamic, right now you have to restart the server to get the choices
    CATEGORY_CHOICES = [(category.pk, category.title) for category in Category.objects.all()]
    
    caption = forms.CharField()
    image_url = forms.URLField()
    categories = forms.MultipleChoiceField(widget=CheckboxSelectMultiple, choices=CATEGORY_CHOICES)
    
    def clean_image_url(self):
        """
        Check that the image url is valid.
        See: http://stackoverflow.com/questions/2486145/python-check-if-url-to-jpg-exists
        """
        url_parts = urlparse(self.cleaned_data['image_url'])
        try:
            conn = httplib.HTTPConnection(url_parts[1])
            conn.request('HEAD', url_parts[2])
            response = conn.getresponse()
            conn.close()
        except:
            raise forms.ValidationError("Please enter a valid image file url.")
        
        if response.status != 200:
            raise forms.ValidationError("Please enter a valid image file url.")
        return self.cleaned_data['image_url']
    
class RegistrationForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password_match = forms.CharField(widget=forms.PasswordInput, label="Confirm")
    
    def clean_email(self):
        """
        Custom form validation that verifies the email 
        address is unique.
        """
        try:
            User.objects.get(email=self.cleaned_data['email'])
            raise forms.ValidationError("That email address has already been registered!")
        except User.DoesNotExist:
            pass
        return self.cleaned_data['email']
    
    def clean_password_match(self):
        """
        Custom form validation that verifies the entered passwords
        match.
        """
        match = self.cleaned_data['password_match']
        password = self.cleaned_data['password']
        
        if password != '' and match != password:
            raise forms.ValidationError("Passwords did not match!")
        return match