"""internProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from accounts import views as accounts_views
from django.contrib.auth import views as auth_views
from lists.views import HomeView, AddPlaylistView, AddSongView, AddArtistView, UserProfileView, \
    PlaylistInfoView, \
    ArtistInfoView, LikeUnlikeView, RemovePlaylistView, SearchbarView, RemoveSongView, \
    SubscribeUnsubscribeView, AddContributerView, BlockUnblockArtistView
from news.views import ArticleInfoView, NewsView, AddReplyView, AddCommentView
from events.views import EventView, EventInfoView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', accounts_views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('', HomeView.as_view(), name='home'),
    path('addsong/<pk>/', AddSongView.as_view(), name='addsong'),
    path('addplaylist/', AddPlaylistView.as_view(), name='addplaylist'),
    path('addartist/', AddArtistView.as_view(), name='addartist'),
    path('userprofile/<pk>/', UserProfileView.as_view(), name='userprofile'),
    path('playlistinfo/<pk>/', PlaylistInfoView.as_view(), name='playlistinfo'),
    path('artistinfo/<pk>/', ArtistInfoView.as_view(), name='artistinfo'),
    path('likeunlike/', LikeUnlikeView.as_view(), name='like_unlike'),
    path('removeList/', RemovePlaylistView.as_view(), name='removelist'),
    path('searchbar/', SearchbarView.as_view(), name='searchbar'),
    path('removesong/<pk>/', RemoveSongView.as_view(), name='removesong'),
    path('subscribe/', SubscribeUnsubscribeView.as_view(), name='subscribe'),
    path('news/', NewsView.as_view(), name='news'),
    path('events/', EventView.as_view(), name='events'),
    path('articleinfo/<pk>/', ArticleInfoView.as_view(), name='articleinfo'),
    path('eventinfo/<pk>/', EventInfoView.as_view(), name='eventinfo'),
    path('addcontributor/<pk>/', AddContributerView.as_view(), name='addcontributor'),
    path('blockunblock/', BlockUnblockArtistView.as_view(), name='block_unblock'),
    path('addreply/<pk>/', AddReplyView.as_view(), name='addreply'),
    path('addcomment/<pk>/', AddCommentView.as_view(), name='addcomment'),
]
