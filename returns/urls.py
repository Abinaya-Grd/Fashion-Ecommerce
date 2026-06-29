from django.urls import path

from .views import (
    ReturnListCreateView,
    ReturnDetailView,
    CancelReturnView,
    ApproveReturnView,
    RejectReturnView,
)

urlpatterns = [

    
    path('', ReturnListCreateView.as_view()),
    path('/<int:pk>', ReturnDetailView.as_view()),
    path('/<int:pk>/cancel', CancelReturnView.as_view()),

   
    path('/<int:pk>/approve', ApproveReturnView.as_view()),
    path('/<int:pk>/reject', RejectReturnView.as_view()),
]