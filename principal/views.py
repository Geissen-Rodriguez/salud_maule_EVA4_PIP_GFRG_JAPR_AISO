from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
import uuid
from .models import PersonalSalud, TokenRecuperacionCuenta


class InicioView(TemplateView):
    template_name = "inicio.html"


class AccesoView(LoginView):
    template_name = "login.html"


class SalidaView(LogoutView):
    next_page = reverse_lazy('login')


class RecuperacionView(TemplateView):
    template_name = "recuperacion.html"

    def post(self, request, *args, **kwargs):
        valor = request.POST.get('token')
        try:
            t = TokenRecuperacionCuenta.objects.get(token=valor, activo=True)
            t.activo = False
            t.save()
            messages.success(request, "Token validado y desactivado.")
        except TokenRecuperacionCuenta.DoesNotExist:
            messages.error(request, "Token inválido o ya usado.")
        return redirect('recuperacion')


class PerfilEditarView(UpdateView):
    model = PersonalSalud
    fields = ['cargo', 'correo_institucional']
    template_name = "perfil_editar.html"
    success_url = reverse_lazy('inicio')


class SolicitarTokenView(View):
    def get(self, request):
        return render(request, 'solicitar_token.html')

    def post(self, request):
        rut = request.POST.get('rut')

        try:
            persona = PersonalSalud.objects.get(rut=rut)

            # Generar token
            token_str = str(uuid.uuid4())[:8]

            # Guardar token asociado al usuario
            TokenRecuperacionCuenta.objects.create(
                usuario=persona.usuario,
                token=token_str,
                activo=True
            )

            return render(request, 'token_generado.html', {'token': token_str})

        except PersonalSalud.DoesNotExist:
            return render(request, 'solicitar_token.html', {
                'error': 'RUT no encontrado'
            })
