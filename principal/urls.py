from django.urls import path
from .views import InicioView, AccesoView, SalidaView, RecuperacionView, PerfilEditarView, SolicitarTokenView

urlpatterns = [
    path('', InicioView.as_view(), name='inicio'),
    path('login/', AccesoView.as_view(), name='login'),
    path('logout/', SalidaView.as_view(), name='logout'),
    path('recuperacion/', RecuperacionView.as_view(), name='recuperacion'),
    path('perfil/<int:pk>/editar/', PerfilEditarView.as_view(), name='perfil_editar'),
    path('solicitar-token/', SolicitarTokenView.as_view(), name='solicitar_token'), 
]
