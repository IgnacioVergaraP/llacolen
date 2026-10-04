from flask import Blueprint, g, request

from app.utils.responses import ok, created
from app.utils.security.decorators import requiere_auth
from app.blueprints.progreso.schemas import (
    validar_crear_serie_payload,
    validar_actualizar_serie_payload,
    validar_query_ejercicio,
    validar_query_fecha,
)
from app.blueprints.progreso import services

bp = Blueprint("progreso", __name__)


@bp.get("")
@requiere_auth
def listar():
    return ok(services.listar_historial(g.usuario_actual.id))


@bp.post("")
@requiere_auth
def crear():
    data = request.get_json(silent=True) or {}
    payload = validar_crear_serie_payload(data)
    resultado = services.crear_serie(
        g.usuario_actual.id,
        g.usuario_actual.gimnasio_id,
        payload,
    )
    return created(resultado)


@bp.get("/evolucion")
@requiere_auth
def evolucion():
    ejercicio = validar_query_ejercicio(request.args.get("ejercicio"))
    return ok(services.obtener_evolucion(g.usuario_actual.id, ejercicio))


@bp.get("/sesion")
@requiere_auth
def sesion():
    ejercicio = validar_query_ejercicio(request.args.get("ejercicio"))
    fecha = validar_query_fecha(request.args.get("fecha"))
    return ok(services.obtener_sesion(g.usuario_actual.id, ejercicio, fecha))


@bp.patch("/<registro_id>")
@requiere_auth
def actualizar(registro_id: str):
    data = request.get_json(silent=True) or {}
    payload = validar_actualizar_serie_payload(data)
    resultado = services.actualizar_serie(g.usuario_actual.id, registro_id, payload)
    return ok(resultado)