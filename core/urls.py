from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import UserLoginView, dashboard, editor_dashboard, lector_dashboard


urlpatterns = [
    path('', UserLoginView.as_view(), name='login'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/editor/', editor_dashboard, name='editor_dashboard'),
    path('dashboard/lector/', lector_dashboard, name='lector_dashboard'),
]
