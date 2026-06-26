from django.urls import path

from .views import (
    ProductListCreateView,
    ProductDetailView,
    ProductFullCreateView,

    ProductImageListCreateView,
    ProductImageDetailView,

    ColorListCreateView,
    SizeListCreateView,
    ProductVariantListCreateView,

    LatestProductsView,
    FeaturedProductsView,
    BestSellerProductsView,
    RelatedProductsView,
)

urlpatterns = [

    path('', ProductListCreateView.as_view()),
    path('/<int:pk>', ProductDetailView.as_view()),
    path('/create-full', ProductFullCreateView.as_view()),
    path('/latest', LatestProductsView.as_view()),
    path('/featured', FeaturedProductsView.as_view()),
    path('/best-sellers', BestSellerProductsView.as_view()),
    path('/<int:pk>/related', RelatedProductsView.as_view()),
    path('/images', ProductImageListCreateView.as_view()),
    path('/images/<int:pk>', ProductImageDetailView.as_view()), 
    path('/colors', ColorListCreateView.as_view()),
    path('/sizes', SizeListCreateView.as_view()),
    path('/variants', ProductVariantListCreateView.as_view()),
]