from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import GameKey


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse e-mail")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class ActivateGameKeyForm(forms.Form):
    key = forms.CharField(max_length=50, required=True, label="Clé de jeu")

    def clean_key(self):
        key = self.cleaned_data['key']
        try:
            game_key = GameKey.objects.get(key=key)
            if game_key.activated:
                raise forms.ValidationError("Cette clé a déjà été activée.")
            return game_key
        except GameKey.DoesNotExist:
            raise forms.ValidationError("Clé de jeu invalide.")