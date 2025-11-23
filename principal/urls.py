from django.urls import path
from django.contrib.auth import views as auth_views

# Importación esencial del formulario personalizado para la doble verificación de correo.
from .forms import CustomPasswordResetForm 

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

    # ================================
    #  RECUPERACIÓN DE CONTRASEÑA DJANGO
    #  (usa User.email O PersonalSalud.correo_institucional)
    # ================================
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
            # Se aplica el formulario que busca en ambas tablas de correo
            form_class=CustomPasswordResetForm 
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