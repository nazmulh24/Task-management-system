from django import forms
import re
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.models import Group, Permission
from tasks.forms import StyleFormMixin
from users.models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()


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


class LoginForm(StyleFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AssignRoleForm(StyleFormMixin, forms.Form):
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(), empty_label="Select Role"
    )


class CreateGroupForm(StyleFormMixin, forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Assign Permissions",
    )

    class Meta:
        model = Group
        fields = ["name", "permissions"]


class CustomPasswordChangeForm(StyleFormMixin, PasswordChangeForm):
    pass


class CustomPasswordResetForm(StyleFormMixin, PasswordResetForm):
    pass


class CustomConfirmPasswordForm(StyleFormMixin, SetPasswordForm):
    pass


"""
class EditProfileForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]

    bio = forms.CharField(required=False, widget=forms.Textarea, label="Bio")
    profile_img = forms.ImageField(required=False, label="Profile Image")

    def __init__(self, *args, **kwargs):
        self.userprofile = kwargs.pop("userprofile", None)
        super().__init__(*args, **kwargs)

        # ToDo: Handle Error

        if self.userprofile:
            self.fields["bio"].initial = self.userprofile.bio
            self.fields["profile_img"].initial = self.userprofile.profile_img

    def save(self, commit=True):
        user = super().save(commit=False)

        if self.userprofile:
            self.userprofile.bio = self.cleaned_data.get("bio")
            self.userprofile.profile_img = self.cleaned_data.get("profile_img")

            if commit:
                self.userprofile.save()

        if commit:
            user.save()

        return user
"""


class EditProfileForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "bio", "profile_img"]
