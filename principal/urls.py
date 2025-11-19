from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
    InicioView, AccesoView, SalidaView,
    RecuperacionView, PerfilEditarView, SolicitarTokenView
)

urlpatterns = [
    path('', InicioView.as_view(), name='inicio'),
    path('login/', AccesoView.as_view(), name='login'),
    path('logout/', SalidaView.as_view(), name='logout'),
    path('recuperacion/', RecuperacionView.as_view(), name='recuperacion'),
    path('perfil/<int:pk>/editar/', PerfilEditarView.as_view(), name='perfil_editar'),
    path('solicitar-token/', SolicitarTokenView.as_view(), name='solicitar_token'),

   
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html'
        ),
        name='password_reset'
    ),

    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
