# Generated by Django 2.2.24 on 2021-08-23 11:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('name', models.CharField(max_length=180)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('blocked', models.ManyToManyField(related_name='blocked_artists', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('likeNumber', models.PositiveIntegerField(auto_created=True, default=0)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('genre', models.CharField(choices=[('Classic', 'Classic'), ('Rock', 'Rock'), ('Indie', 'Indie'), ('Punk', 'Punk'), ('Metal', 'Metal'), ('Country', 'Country'), ('Jazz', 'Jazz'), ('Blues', 'Blues'), ('Grunge', 'Grunge'), ('Pop', 'Pop'), ('Rap', 'Rap'), ('Techno', 'Techno')], max_length=100)),
                ('artist', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lists.Artist')),
                ('likes', models.ManyToManyField(related_name='liked', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('songNumber', models.SmallIntegerField(auto_created=True, default=0)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=180)),
                ('description', models.CharField(max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('editable', models.BooleanField(default=True)),
                ('poster', models.ImageField(default='static/images/user-1.jpg', null=True, upload_to='static/images/')),
                ('creators', models.ManyToManyField(related_name='playlists', to=settings.AUTH_USER_MODEL)),
                ('songs', models.ManyToManyField(related_name='playlist', to='lists.Song')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
