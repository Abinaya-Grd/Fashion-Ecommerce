from django.urls import path

from .views import (
    WishlistView,
    AddToWishlistView,
    RemoveWishlistItemView,
    ClearWishlistView,
)

urlpatterns = [

    path('', WishlistView.as_view()),

    path('/add', AddToWishlistView.as_view()),

    path('/remove/<int:pk>', RemoveWishlistItemView.as_view()),

    path('/clear', ClearWishlistView.as_view()),
]