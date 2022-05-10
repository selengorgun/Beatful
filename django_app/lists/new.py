import spotipy

from spotipy.oauth2 import SpotifyClientCredentials

import pandas as pd

import requests

from lists.models import Artist, Song, List

from events.models import Event

from news.models import Article

cid = '33ba73d2a49542b3b0f9ed39a347765a'
secret = '9de3d7434da64e82b8cdb1d0cf948d17'

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_track_names(playlist_id):
    song_names = []
    playlist = sp.playlist(playlist_id)
    for item in playlist['tracks']['items']:
        track = item['track']
        song_names.append(track['name'])
    return song_names


def get_artist_names(playlist_id):
    artist_names = []
    playlist = sp.playlist(playlist_id)
    for item in playlist['tracks']['items']:
        track = item['track']
        artist_names.append(track['artists'][0]['name'])
    return artist_names


def create(playlist_id):
    playlist = sp.playlist(playlist_id)
    for item in playlist['tracks']['items']:
        track = item['track']
        if Artist.objects.filter(name=track['artists'][0]['name']).count() == 0:
            Artist.objects.create(name=track['artists'][0]['name'])
        artist = Artist.objects.get(name=track['artists'][0]['name'])
        if Song.objects.filter(name=track['name']).count() == 0:
            Song.objects.create(name=track['name'], genre="Techno", artist=artist)


def get_news():
    URL = "https://rapidapi.p.rapidapi.com/api/search/NewsSearchAPI"
    HEADERS = {
        "x-rapidapi-host": "contextualwebsearch-websearch-v1.p.rapidapi.com",
        "x-rapidapi-key": "ea6579ee47msh240bad8cd862d74p119032jsn8eb888550fda"
    }

    query = "music"
    page_number = 1
    page_size = 10
    auto_correct = True
    safe_search = False
    with_thumbnails = True
    from_published_date = ""
    to_published_date = ""

    querystring = {"q": query,
                   "pageNumber": page_number,
                   "pageSize": page_size,
                   "autoCorrect": auto_correct,
                   "safeSearch": safe_search,
                   "withThumbnails": with_thumbnails,
                   "fromPublishedDate": from_published_date,
                   "toPublishedDate": to_published_date}

    response = requests.get(URL, headers=HEADERS, params=querystring).json()

    # print(response)

    total_count = response["totalCount"]

    for web_page in response["value"]:
        url = web_page["url"]
        title = web_page["title"]
        description = web_page["description"]
        body = web_page["body"]
        date_published = web_page["datePublished"]
        language = web_page["language"]
        is_safe = web_page["isSafe"]
        provider = web_page["provider"]["name"]

        image_url = web_page["image"]["url"]
        image_height = web_page["image"]["height"]
        image_width = web_page["image"]["width"]
        image = web_page["image"]

        thumbnail = web_page["image"]["thumbnail"]
        thumbnail_height = web_page["image"]["thumbnailHeight"]
        thumbnail_width = web_page["image"]["thumbnailWidth"]

        Article.objects.create(title=title, description=description, body=body, publication_date=date_published,
                               author=provider, thumbnail=image)

        # Event.objects.create(title=title, description=description, body=body, date=date_published, site=url)

        # print("Url: {}. Title: {}. Published Date: {}.".format(url, title, date_published))


def call_playlist(creator, playlist_id):
    # step1

    playlist_features_list = ["artist", "album", "track_name", "track_id", "danceability", "energy", "key", "loudness",
                              "mode", "speechiness", "instrumentalness", "liveness", "valence", "tempo", "duration_ms",
                              "time_signature"]

    playlist_df = pd.DataFrame(columns=playlist_features_list)

    # step2

    playlist = sp.user_playlist_tracks(creator, playlist_id)["items"]
    # playlist = sp.playlist_tracks(playlist_id)
    for track in playlist:
        # Create empty dict
        playlist_features = {}
        # Get metadata
        playlist_features["artist"] = track["track"]["album"]["artists"][0]["name"]
        playlist_features["album"] = track["track"]["album"]["name"]
        playlist_features["track_name"] = track["track"]["name"]
        playlist_features["track_id"] = track["track"]["id"]

        artist_name = track["track"]["album"]["artists"][0]["name"]
        song_name = track["track"]["name"]

        for a in Artist.objects.all():
            if a.name != artist_name:
                Artist.objects.create(name=artist_name)

        artist = Artist.objects.get(name=artist_name)

        for s in Song.objects.all():
            if s.name != song_name:
                Song.objects.create(name=song_name, genre="Metal", artist=artist)

        # Get audio features
        audio_features = sp.audio_features(playlist_features["track_id"])[0]
        for feature in playlist_features_list[4:]:
            playlist_features[feature] = audio_features[feature]

        # Concat the dfs
        track_df = pd.DataFrame(playlist_features, index=[0])
        playlist_df = pd.concat([playlist_df, track_df], ignore_index=True)

    # Step 3

    return playlist_df
