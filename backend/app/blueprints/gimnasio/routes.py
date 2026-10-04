from flask import Blueprint, g

from app.utils.responses import ok
from app.utils.security.decorators import requiere_auth
from app.blueprints.gimnasio import services

bp = Blueprint("gimnasio", __name__)


@bp.get("/config")
@requiere_auth
def config():
    """Configuración visual del gimnasio del usuario autenticado."""
    return ok(services.obtener_config(g.usuario_actual.gimnasio_id))