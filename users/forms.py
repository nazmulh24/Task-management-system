from django import forms
import re
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from tasks.forms import StyleFormMixin


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        for fieldName in ["username", "password1", "password2"]:
            self.fields[fieldName].help_text = None


class CustomRegisterForm(StyleFormMixin, forms.ModelForm):
    pass1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    pass2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "pass1",
            "pass2",
        ]

    def clean_email(self):  # ---------> Duplicate Email Error
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email Already Exists.")

        return email

    def clean_pass1(self):  # -------------------> Field Error
        pass1 = self.cleaned_data.get("pass1")
        errors = []

        if len(pass1) < 8:
            errors.append("Password must be at least 8 characters.")
        if not re.search(r"[!@#$%^&*()\-_=+]", pass1):
            errors.append("Password must contain at least one special character.")

        if errors:
            raise forms.ValidationError(errors)

        return pass1

    def clean(self):  # ---------------------> Non Field Error
        cleaned_data = super().clean()
        pass1 = cleaned_data.get("pass1")
        pass2 = cleaned_data.get("pass2")

        if pass1 != pass2:
            raise forms.ValidationError("Password do not match.")

        return cleaned_data


#
