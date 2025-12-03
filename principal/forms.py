# forms.py

from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

# 1. Tu Modelo Personalizado
from .models import PersonalSalud 

# 2. Utilidades Requeridas para el Envío Manual (save)
from django.core.mail import send_mail
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site



class CustomPasswordResetForm(PasswordResetForm):
    
    # ----------------------------------------------------
    # I. get_users() - LA BÚSQUEDA DUAL
    # ----------------------------------------------------
    def get_users(self, email):
        # ... (Tu lógica para encontrar usuario por auth_user.email O PersonalSalud.correo_institucional)
        UserModel = get_user_model()
        users_by_auth_email = UserModel._default_manager.filter(email__iexact=email, is_active=True)
        users_by_perfil_email = UserModel.objects.none()
        try:
            user_ids = PersonalSalud.objects.filter(correo_institucional__iexact=email).values_list('usuario_id', flat=True)
            if user_ids:
                users_by_perfil_email = UserModel._default_manager.filter(id__in=list(user_ids), is_active=True)
        except Exception:
            pass
        return (users_by_auth_email | users_by_perfil_email).distinct()

    def clean_email(self):
        email = self.cleaned_data["email"]
        users = self.get_users(email)
        
        # Si no encuentra al usuario por NINGUNO de los dos correos, lanza el error
        if not users.exists():
            raise forms.ValidationError(
                self.error_messages['unknown'],
                code='unknown',
            )
        return email

    # ----------------------------------------------------
    # III. save() - EL ENVÍO FORZADO
    # ----------------------------------------------------
    def save(self, request, **kwargs):
        email_input = self.cleaned_data["email"]
        users = list(self.get_users(email_input)) 
        
        if not users:
            return

        current_site = get_current_site(request)
        
        for user in users:
            # 1. DETERMINAR EL CORREO DE DESTINO (SIEMPRE EL INSTITUCIONAL)
            recipient_email = None
            try:
                perfil = PersonalSalud.objects.get(usuario=user)
                recipient_email = perfil.correo_institucional # <-- CORREO INSTITUCIONAL
            except PersonalSalud.DoesNotExist:
                recipient_email = user.email
            
            # 2. GENERAR Y ENVIAR
            if recipient_email:
                c = {
                    'email': recipient_email, 
                    'domain': current_site.domain,
                    'site_name': current_site.name,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'user': user, # Objeto User de auth_user (andres)
                    'token': default_token_generator.make_token(user),
                    'protocol': 'https' if request.is_secure() else 'http',
                    'current_site': current_site,
                }
                
                subject = loader.render_to_string(kwargs.get('subject_template_name'), c)
                subject = ''.join(subject.splitlines())
                body = loader.render_to_string(kwargs.get('email_template_name'), c)
                
                send_mail(
                    subject, 
                    body, 
                    kwargs.get('from_email'), 
                    [recipient_email], # <--- DESTINO ES EL INSTITUCIONAL
                    fail_silently=False
                )
                
        return