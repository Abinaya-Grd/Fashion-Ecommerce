from django.urls import path

from .views import (
    BannerListCreateView,
    BannerDetailView,
    ActiveBannerView,
    WebBannerView,
    MobileBannerView,
)

urlpatterns = [

    path('', BannerListCreateView.as_view()),

    path('/<int:pk>', BannerDetailView.as_view()),

    path('/active', ActiveBannerView.as_view()),

    path('/web', WebBannerView.as_view()),

    path('/mobile', MobileBannerView.as_view()),

]