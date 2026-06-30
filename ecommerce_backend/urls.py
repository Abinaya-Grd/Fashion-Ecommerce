"""
URL configuration for ecommerce_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from categories.views import (
    CategoryListCreateView,
    CategoryDetailView,
    SubCategoryListCreateView,
    SubCategoryDetailView,
    ProductStyleListCreateView,
    ProductStyleDetailView,
    BrandListCreateView,
    BrandDetailView,
)



urlpatterns = [

    path('admin/', admin.site.urls),

    path('api/accounts/', include('accounts.urls')),

    path('api/categories', CategoryListCreateView.as_view()),
    path('api/categories/<int:pk>', CategoryDetailView.as_view()),

    path('api/subcategories', SubCategoryListCreateView.as_view()),
    path('api/subcategories/<int:pk>', SubCategoryDetailView.as_view()),

    path('api/productstyles', ProductStyleListCreateView.as_view()),
    path('api/productstyles/<int:pk>', ProductStyleDetailView.as_view()),

    path('api/brands', BrandListCreateView.as_view()),
    path('api/brands/<int:pk>', BrandDetailView.as_view()),

    # Products
    path('api/products', include('products.urls')),

    path('api/cart', include('cart.urls')),
    path('api/wishlist', include('wishlist.urls')),
    path('api/orders', include('orders.urls')),
    path('api/payments', include('payments.urls')),
    path('api/coupons', include('coupons.urls')),
    path('api/reviews', include('reviews.urls')),
    path('api/invoices', include('invoices.urls')),
    path('api/dashboard', include('dashboard.urls')),
    path('api/returns', include('returns.urls')),
    path('api/notifications', include('notifications.urls')),
    path('api/wallet', include('wallet.urls')),
    path('api/reports', include('reports.urls')),
    path('api/banners', include('banners.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
#     path('api/categories/', include('categories.urls')),
#     path('api/products/', include('products.urls')),
#     path('api/cart/', include('cart.urls')),
#     path('api/wishlist/', include('wishlist.urls')),
#     path('api/orders/', include('orders.urls')),
#     path('api/payments/', include('payments.urls')),
#     path('api/coupons/', include('coupons.urls')),
#     path('api/reviews/', include('reviews.urls')),
#     
#     path('api/dashboard/', include('dashboard.urls')),
# ]
