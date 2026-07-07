from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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

from ecommerce_backend.views import home


schema_view = get_schema_view(
    openapi.Info(
        title="Fashion Ecommerce API",
        default_version="v1",
        description="Production Ready Fashion Ecommerce Backend API",
        contact=openapi.Contact(
            email="mounttowntech@gmail.com"
        ),
        license=openapi.License(
            name="MIT"
        ),
    ),
    public=True,
    permission_classes=(
        permissions.AllowAny,
    ),
)


urlpatterns = [
     path("", home),
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
    path('api/inventory', include('inventory.urls')),
    path('api/suppliers', include('suppliers.urls')),
    path('api/purchases', include('purchases.urls')),
    path('api/purchase-returns', include('purchase_returns.urls')),

    path(
        'swagger/',
        schema_view.with_ui(
            'swagger',
            cache_timeout=0
        ),
        name='schema-swagger-ui',
    ),

    path(
        'redoc/',
        schema_view.with_ui(
            'redoc',
            cache_timeout=0
        ),
        name='schema-redoc',
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )