from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


def is_admin_user(user):
    """Verifica si el usuario es administrador o superusuario."""
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name='ADMINISTRADOR').exists()


def is_conductor_user(user):
    """Verifica si el usuario pertenece al grupo CONDUCTOR."""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name='CONDUCTOR').exists()


def admin_required(view_func):
    """
    Decorador para vistas exclusivas de administradores.
    Si el usuario no ha iniciado sesión, redirige a login.
    Si está autenticado pero no es administrador, deniega el acceso.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not is_admin_user(request.user):
            return HttpResponseForbidden("Acceso denegado: Se requiere rol de Administrador para ver este módulo.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def conductor_required(view_func):
    """
    Decorador para vistas de conductor.
    Si el usuario no ha iniciado sesión, redirige a login.
    Si está autenticado pero no es conductor (ni admin), deniega el acceso.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (is_conductor_user(request.user) or is_admin_user(request.user)):
            return HttpResponseForbidden("Acceso denegado: Se requiere rol de Conductor o Administrador.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
