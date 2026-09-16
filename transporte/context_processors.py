from .decorators import is_admin_user, is_conductor_user


def role_context(request):
    """
    Inyecta datos de rol y perfil del usuario autenticado en todos los templates.
    """
    user = request.user
    if not user.is_authenticated:
        return {
            'is_admin': False,
            'is_conductor': False,
            'user_role': '',
            'user_role_display': '',
            'user_display_name': '',
            'user_initials': '',
        }

    is_adm = is_admin_user(user)
    is_cond = is_conductor_user(user)

    if is_adm:
        role_label = 'ADMINISTRADOR'
        role_display = 'Administrador de Flota'
    elif is_cond:
        role_label = 'CONDUCTOR'
        role_display = 'Conductor Operativo'
    else:
        role_label = 'USUARIO'
        role_display = 'Usuario'

    display_name = user.get_full_name() or user.username
    initials = ''.join([part[0].upper() for part in display_name.split()[:2]]) or user.username[:2].upper()

    return {
        'is_admin': is_adm,
        'is_conductor': is_cond,
        'user_role': role_label,
        'user_role_display': role_display,
        'user_display_name': display_name,
        'user_initials': initials,
    }
