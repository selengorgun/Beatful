from django.db import models
from django.contrib.auth.models import User


class Artist(models.Model):
    name = models.CharField(max_length=180)
    id = models.AutoField(primary_key=True)
    blocked = models.ManyToManyField(User, related_name='blocked_artists')

    def __str__(self):
        return self.name


class Song(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    genres = [("Classic", "Classic"), ("Rock", "Rock"), ("Indie", "Indie"), ("Punk", "Punk"), ("Metal", "Metal"),
              ("Country", "Country"), ("Jazz", "Jazz"), ("Blues", "Blues"), ("Grunge", "Grunge"),
              ("Pop", "Pop"), ("Rap", "Rap"), ("Techno", "Techno")]
    genre = models.CharField(max_length=100, choices=genres)
    artist = models.ForeignKey(Artist, blank=False, null=True, on_delete=models.CASCADE)
    likeNumber = models.PositiveIntegerField(auto_created=True, default=0)
    likes = models.ManyToManyField(User, related_name='liked')

    def __str__(self):
        return self.name


class List(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=180)
    description = models.CharField(max_length=500)
    songNumber = models.SmallIntegerField(auto_created=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    creators = models.ManyToManyField(User, related_name="playlists")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='+')
    songs = models.ManyToManyField(Song, related_name="playlist")
    editable = models.BooleanField(default=True)
    poster = models.ImageField(upload_to='static/images/', null=True, default='static/images/user-1.jpg')

    def __str__(self):
        return self.title

    def songs_to_add(self):
        songs = list()
        for song in Song.objects.all():
            if song not in self.songs.all():
                songs.append(song)
        return songs
