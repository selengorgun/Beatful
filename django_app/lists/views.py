import random
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np
from .models import List, Song, Artist
from django.views import View
from .forms import AddPlayListForm, AddSongForm, AddArtistForm, AddContributorForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from accounts.models import Profile
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from news.models import Article
from events.models import Event

# numpy, sklearn, random, django


def k_means_song(user):
    scalar = StandardScaler()

    array = []
    labels = []

    songs = user.liked.all()
    cluster_number = 1

    if len(songs) >= 20:
        cluster_number = 2
    elif len(songs) >= 40:
        cluster_number = 3

    genres = {}
    i = 0

    for genre in Song.genres:
        genres[genre[0]] = i
        i += 1

    i = 0
    for song in songs:
        labels.append(song.id)
        array_item = [genres[song.genre], song.artist.pk]
        array.append(array_item)
        i += 1

    scaled_songs = scalar.fit_transform(array)

    kmeans = KMeans(init='k-means++', n_clusters=cluster_number, n_init=10, max_iter=300, random_state=42)

    song_clusters = kmeans.fit(scaled_songs).labels_

    cluster_labels = [[] for i in range(3)]

    for i, j in enumerate(song_clusters):
        cluster_labels[j].append(labels[i])

    return song_clusters, kmeans, cluster_labels


def calculate_distance(centroid, centroid_friend):
    centroid_x = centroid[0]
    centroid_y = centroid[1]
    centroid_list = np.array(centroid_x, centroid_y)

    centroid_friend_x = centroid_friend[0]
    centroid_friend_y = centroid_friend[1]
    centroid_friend_list = np.array(centroid_friend_x, centroid_friend_y)

    dist = np.sqrt(np.sum(np.square(centroid_list - centroid_friend_list)))

    return dist


def recommend_song(user):
    song_clusters, kmeans, cluster_labels = k_means_song(user)
    centroids = kmeans.cluster_centers_
    songs_to_recommend = []

    friends = list(Profile.objects.get(user=user).subscriptions.all())

    if len(friends) > 0:
        friend = random.sample(friends, 1)[0]
    else:
        friend = User.objects.get(is_superuser=True)

    song_clusters_friend, kmeans_friend, cluster_labels_friend = k_means_song(friend)
    centroids_friend = kmeans_friend.cluster_centers_

    centroid = random.sample(list(centroids), 1)[0]
    centroid_friend = centroids_friend[0]

    distance = calculate_distance(centroid, centroid_friend)

    counter = 0
    for c in centroids_friend:
        new_distance = calculate_distance(centroid, c)
        if new_distance < distance:
            distance = new_distance
            songs_to_recommend = []
            for song_id in list(cluster_labels_friend)[counter]:
                song = Song.objects.get(id=song_id)
                playlist = List.objects.get(creators__username__contains=user.username, title="Recommended Songs")
                if song not in user.liked.all() and song not in playlist.songs.all():
                    songs_to_recommend.append(song)

        counter += 1

    return songs_to_recommend


class HomeView(View):
    def get(self, request):
        lists = list()

        for item in List.objects.all():
            for person in item.creators.all():
                if person.is_superuser and not item.editable:
                    lists.append(item)

        songs_ordered = Song.objects.order_by('-likeNumber')[0:50]
        if request.user.is_authenticated:
            liked_list = List.objects.get(creators__username__contains=request.user.username, title="Liked Songs")
        else:
            liked_list = []

        return render(request, 'home.html', {'lists': lists, 'songs': songs_ordered, 'liked_list': liked_list})


class UserProfileView(View):
    @method_decorator(login_required)
    def get(self, request, pk):
        user = request.user
        profile = Profile.objects.get(pk=pk)
        subs = profile.subscriptions.all()
        uneditable_lists = List.objects.filter(editable=False, creators__username__contains=profile.user.username)
        editable_lists = List.objects.filter(editable=True, creators__username__contains=profile.user.username)
        blocked_artists = profile.user.blocked_artists.all()

        return render(request, 'user_profile.html', {'user': user, 'editableLists': editable_lists,
                                                     'uneditableLists': uneditable_lists, 'subs': subs,
                                                     'profile': profile, 'blocked_artists': blocked_artists})


class PlaylistInfoView(View):
    @method_decorator(login_required)
    def get(self, request, pk):
        list_obj = get_object_or_404(List, pk=pk)
        creators = list_obj.creators
        liked_list = List.objects.get(creators__username__contains=request.user.username, title="Liked Songs")
        user = request.user

        song_list = []
        for song in list_obj.songs.all():
            if user not in song.artist.blocked.all():
                song_list.append(song)

        page = request.GET.get('page', 1)
        paginator = Paginator(song_list, 10)
        try:
            songs = paginator.page(page)
        except PageNotAnInteger:
            songs = paginator.page(1)
        except EmptyPage:
            songs = paginator.page(paginator.num_pages)

        # recommendations = set()
        # if user in list_obj.creators.all():
        #    for person in list_obj.creators.all():
        #        rec_list = List.objects.get(creators__username__contains=person.username, title="Recommended Songs")
        #        for song in rec_list.songs.all():
        #            recommendations.add(song)

        return render(request, 'list_information.html', {'list': list_obj, 'songs': songs, 'likedList': liked_list,
                                                         'creators': creators})


class BlockUnblockArtistView(View):
    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        if request.method == 'POST':
            artist = get_object_or_404(Artist, id=request.POST.get('artist_id'))
            if user in artist.blocked.all():
                artist.blocked.remove(user)
                artist.save()
            else:
                artist.blocked.add(user)
                artist.save()

        return JsonResponse({'success': True}, status=200)


class LikeUnlikeView(View):
    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        song = get_object_or_404(Song, id=request.POST.get('song_id'))
        liked_list = List.objects.get(creators__username__contains=user.username, title="Liked Songs")

        songs = liked_list.songs
        if song in songs.all():
            song.likes.remove(user)
            liked_list.songs.remove(song)
            liked_list.songNumber -= 1
            song.likeNumber -= 1
        else:
            song.likes.add(user)
            liked_list.songs.add(song)
            song.likeNumber += 1
            liked_list.songNumber += 1

        song.save()
        liked_list.save()

        recommended_list = List.objects.get(creators__username__contains=user.username, title="Recommended Songs")
        recommended_songs = recommend_song(user)
        for song in recommended_songs:
            recommended_list.songs.add(song)
            recommended_list.songNumber += 1

        recommended_list.save()

        return JsonResponse({'success': True}, status=200)


class AddContributerView(View):
    @method_decorator(login_required)
    def get(self, request, pk):
        form = AddContributorForm()
        friends = request.user.profile.subscriptions.all()
        list_obj = List.objects.get(pk=pk)

        return render(request, 'add_song.html', {'form': form, 'friends': friends, 'list': list_obj})

    @method_decorator(login_required)
    def post(self, request, pk):
        if request.method == 'POST':
            list_obj = List.objects.get(pk=pk)
            form = AddContributorForm(request.POST)
            if form.is_valid():
                for person in form.cleaned_data['creators']:
                    if person not in list_obj.creators.all():
                        list_obj.creators.add(person)
                list_obj.updated_by = request.user
                list_obj.save()
                return HttpResponseRedirect(reverse('playlistinfo', args=[pk]))
            else:
                songs = list_obj.songsToAdd()

        return render(request, 'add_song.html', {'songs': songs})


class ArtistInfoView(View):
    def get(self, request, pk):
        artist = get_object_or_404(Artist, pk=pk)
        songs = Song.objects.filter(artist=artist)
        liked_list = List.objects.get(creators__username__contains=request.user.username, title="Liked Songs")

        return render(request, 'artist_profile.html', {'artist': artist, 'songs': songs, 'liked_list': liked_list})


class RemovePlaylistView(View):
    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        list_obj = get_object_or_404(List, id=request.POST.get('remove_btn'))
        list_obj.delete()

        return HttpResponseRedirect(reverse('userprofile', args=[user.pk]))


class RemoveSongView(View):
    @method_decorator(login_required)
    def post(self, request, pk):
        user = request.user
        song = get_object_or_404(Song, id=request.POST.get('remove_btn'))
        list_obj = List.objects.get(pk=pk)
        list_obj.songs.remove(song)
        list_obj.songNumber -= 1
        list_obj.save()
        return HttpResponseRedirect(reverse('playlistinfo', args=[str(pk)]))


class SearchbarView(View):
    @method_decorator(login_required)
    def post(self, request):
        if request.method == "POST":
            searched = request.POST.get('searched')
            user = request.user
            users = User.objects.filter(username__icontains=searched)
            songs = Song.objects.filter(name__icontains=searched)
            playlists = List.objects.filter(title__icontains=searched)
            artists = []
            artist_list = Artist.objects.filter(name__icontains=searched)
            for artist in artist_list:
                if user not in artist.blocked.all():
                    artists.append(artist)

            news = Article.objects.filter(title__icontains=searched)
            events = Event.objects.filter(title__icontains=searched)

            return render(request, 'search.html', {'searched': searched, 'users': users, 'user': user, 'songs': songs,
                                                   'playlists': playlists, 'artists': artists, 'news': news,
                                                   'events': events})
        else:
            return render(request, 'search.html', {})


class SubscribeUnsubscribeView(View):
    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        profile = Profile.objects.get(user=user)
        if request.method == 'POST':
            person = get_object_or_404(Profile, id=request.POST.get('profile_id'))
            if person.user in profile.subscriptions.all():
                profile.subscriptions.remove(person.user)
                person.subNumber -= 1
            else:
                profile.subscriptions.add(person.user)
                person.subNumber += 1
            person.save()
            profile.save()

        return JsonResponse({'success': True}, status=200)


class AddPlaylistView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = AddPlayListForm()

        return render(request, 'add_playlist.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = AddPlayListForm(request.POST)
        if form.is_valid():
            list_obj = form.save(commit=False)
            list_obj.save()
            list_obj.creators.add(request.user)
            list_obj.updated_by = request.user
            list_obj.save()
            form.save_m2m()
            for song in list_obj.songs.all():
                list_obj.songNumber += 1
            list_obj.save()
            return HttpResponseRedirect(reverse('userprofile', args=[request.user.pk]))
        else:
            form = AddPlayListForm()
        return render(request, 'add_playlist.html', {'form': form})


class AddSongView(View):
    @method_decorator(login_required)
    def get(self, request, pk):
        form = AddSongForm()
        songs = List.objects.get(pk=pk).songs.all()

        genres = set()
        for song in songs:
            genres.add(song.genre)

        return render(request, 'add_song.html', {'form': form, 'songs': songs, 'genres': genres})

    @method_decorator(login_required)
    def post(self, request, pk):
        if request.method == 'POST':
            list_obj = List.objects.get(pk=pk)
            form = AddSongForm(request.POST)
            if form.is_valid():
                for song in form.cleaned_data['songs']:
                    if song not in list_obj.songs.all():
                        list_obj.songNumber += 1
                        list_obj.songs.add(song)
                list_obj.updated_by = request.user
                list_obj.save()
                return HttpResponseRedirect(reverse('userprofile', args=[request.user.pk]))
            else:
                songs = list_obj.songsToAdd()

        return render(request, 'add_song.html', {'songs': songs})


class AddArtistView(View):
    @method_decorator(login_required)
    def get(self, request):
        name = Artist.name
        return render(request, 'add_artist.html', {'name': name})

    @method_decorator(login_required)
    def post(self, request):
        if request.method == 'POST':
            form = AddArtistForm(request.POST)
            if form.is_valid():
                artist = form.save(commit=False)
                name = artist.name
                return redirect('home')
        else:
            form = AddArtistForm()

        return render(request, 'add_artist.html', {'form': form})
