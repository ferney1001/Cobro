from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('login'), name='inicio'),

    path('admin/', admin.site.urls),

    path(
        'login/',
        LoginView.as_view(template_name='registration/login.html'),
        name='login'
    ),

    path(
        'logout/',
        LogoutView.as_view(),
        name='logout'
    ),

    path('dashboard/', include('dashboard.urls')),

    path('clientes/', include('clientes.urls')),

    path('prestamos/', include('prestamos.urls')),
]