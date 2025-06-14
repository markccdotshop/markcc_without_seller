from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from django import forms


class CaptchaForm(forms.Form):
    captcha = CaptchaField()

class SignUpForm(UserCreationForm):
    captcha = CaptchaField(error_messages={
        'invalid': 'Invalid CAPTCHA. Please try again.',
        'required': 'Please enter the characters from the image.'
    })

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2', 'captcha')
        error_messages = {
            'username': {
                'unique': "A user with that username already exists. Please choose a different one.",
                'required': 'Username is required.',
                'invalid': 'This username is invalid. Please enter a valid username.'
            },
            'password1': {
                'required': 'Password is required.',
                'password_too_short': 'This password is too short. It must contain at least 8 characters.',
                'password_too_common': 'This password is too common.',
                'password_entirely_numeric': 'This password is entirely numeric.'
            },
            'password2': {
                'required': 'Confirming your password is required.',
                'password_mismatch': "The passwords didn’t match. Please confirm your password again.",
            },
            'captcha': {
                'required': 'CAPTCHA verification is required.',
                'invalid': 'Invalid CAPTCHA. Please try again.'
            },
        }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        # Update field labels for clarity
        self.fields['password1'].label = "Password"
        self.fields['password2'].label = "Confirm Password"
        self.fields['password1'].help_text = 'Your password must contain at least 8 characters and should not be entirely numeric.'
        self.fields['password2'].help_text = 'Re-enter your password for confirmation.'
        self.fields['captcha'].help_text = 'Enter the text shown in the image above to verify you are not a robot.'
        self.fields['captcha'].label = ""

        # Update placeholders for all fields for consistency and clarity
        for fieldname in ['username', 'password1', 'password2', 'captcha']:
            self.fields[fieldname].widget.attrs.update({'placeholder': self.fields[fieldname].label})