from django import forms
from .models import Song, List, Artist
from django.forms import ModelForm


class AddPlayListForm(ModelForm):
    class Meta:
        model = List
        fields = ('title', 'description', 'songs', 'poster')


class AddSongForm(ModelForm):
    class Meta:
        model = List
        fields = ('songs',)


class AddArtistForm(ModelForm):
    class Meta:
        model = Artist
        fields = ('name',)


class AddContributorForm(ModelForm):
    class Meta:
        model = List
        fields = ('creators',)
