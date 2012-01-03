from django import forms
from django.contrib.auth.models import User
from core.models import Category, Image

from django.forms.widgets import CheckboxSelectMultiple


class SubmissionForm(forms.Form):
    caption = forms.CharField()
    image_url = forms.URLField()
    
    def clean_image_url(self):
        """
        Check that the image url is valid.
        See: http://stackoverflow.com/questions/2486145/python-check-if-url-to-jpg-exists
        """
        if not Image.check_url(self.cleaned_data['image_url']):
            raise forms.ValidationError("Please enter a valid image URL!")
        
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