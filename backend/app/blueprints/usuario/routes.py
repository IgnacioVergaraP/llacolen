from flask import Blueprint, g, request

from app.utils.responses import ok
from app.utils.security.decorators import requiere_auth
from app.blueprints.usuario.schemas import validar_actualizar_perfil_payload
from app.blueprints.usuario import services

bp = Blueprint("usuario", __name__)


@bp.get("/perfil")
@requiere_auth
def perfil():
    # El solicitante es siempre el propio usuario autenticado.
    # Su propio rol decide si se filtra notas_profesor.
    return ok(services.obtener_perfil(g.usuario_actual, g.usuario_actual.rol))


@bp.patch("/perfil")
@requiere_auth
def actualizar_perfil():
    data = request.get_json(silent=True) or {}
    payload = validar_actualizar_perfil_payload(data)
    return ok(services.actualizar_perfil(g.usuario_actual, payload))


@bp.get("/resumen")
@requiere_auth
def resumen():
    return ok(services.obtener_resumen(g.usuario_actual))