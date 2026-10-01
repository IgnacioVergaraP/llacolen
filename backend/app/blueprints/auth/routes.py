from flask import Blueprint, g

from app.utils.responses import ok
from app.utils.security.decorators import requiere_auth
from app.blueprints.auth import services

bp = Blueprint("auth", __name__)


@bp.get("/me")
@requiere_auth
def me():
    """
    Devuelve el perfil del usuario autenticado.
    Útil para el frontend para restaurar la sesión tras un refresh:
    el frontend puede llamar a esto con el token de Supabase y obtener
    el perfil completo (incluyendo el rol ya validado por el backend).
    """
    return ok(services.obtener_perfil_actual(g.usuario_actual))