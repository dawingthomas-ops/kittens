from django.urls import path

from . import views

app_name = "kittens"

urlpatterns = [
    path("kittens/", views.KittenListView.as_view(), name="list"),
    path("kittens/<slug:slug>/", views.KittenDetailView.as_view(), name="detail"),
    path("kitten-match/", views.KittenMatchView.as_view(), name="match"),
    path("favorites/", views.FavoritesView.as_view(), name="favorites"),
    path("favorites/cards/", views.FavoritesResultsView.as_view(), name="favorites_cards"),
]
