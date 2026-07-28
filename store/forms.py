from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


INPUT_CLASS = (
    "w-full "
    "bg-[#1b1b1b] "
    "border border-neutral-700 "
    "rounded-xl "
    "px-5 py-4 "
    "text-white "
    "placeholder:text-neutral-500 "
    "focus:outline-none "
    "focus:border-orange-500 "
    "focus:ring-2 "
    "focus:ring-orange-500/30 "
    "transition-all duration-300"
)


class RegisterForm(forms.ModelForm):

    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Full Name",
            }
        )
    )

    whatsapp_number = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "WhatsApp Number",
            }
        )
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Create Password",
            }
        )
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Confirm Password",
            }
        )
    )

    class Meta:

        model = User

        fields = [
            "username",
        ]

        widgets = {

            "username": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Username",
                }
            ),

        }

    def clean(self):

        cleaned_data = super().clean()

        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:

            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data

class LoginForm(AuthenticationForm):

    username = forms.CharField(

        widget=forms.TextInput(

            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Username",
            }

        )

    )

    password = forms.CharField(

        widget=forms.PasswordInput(

            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Password",
            }

        )

    )