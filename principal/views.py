from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
import uuid
from .models import PersonalSalud


class InicioView(TemplateView):
    template_name = "inicio.html"


class AccesoView(LoginView):
    template_name = "login.html"


class SalidaView(LogoutView):
    next_page = reverse_lazy('login')




class PerfilEditarView(UpdateView):
    model = PersonalSalud
    fields = ['cargo', 'correo_institucional']
    template_name = "perfil_editar.html"
    success_url = reverse_lazy('inicio')


