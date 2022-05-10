from django.db import models
from django.contrib.auth.models import User
from lists.models import List, Song, Artist
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    subscriptions = models.ManyToManyField(User, related_name='subscribed')
    subNumber = models.PositiveIntegerField(auto_created=True, default=0)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

        list_r = List.objects.create(title="Recommended Songs", description="Your recommended songs.", editable=False)
        list_r.creators.add(instance)
        list_r.save()

        list_l = List.objects.create(title="Liked Songs", description="Songs you liked", editable=False)
        list_l.creators.add(instance)
        list_l.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
