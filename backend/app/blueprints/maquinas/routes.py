from flask import Blueprint, request

from app.utils.responses import ok
from app.utils.security.decorators import requiere_auth
from app.blueprints.maquinas.schemas import validar_query_musculo
from app.blueprints.maquinas import services

bp = Blueprint("maquinas", __name__)


@bp.get("")
@requiere_auth
def listar():
    musculo = validar_query_musculo(request.args.get("musculo"))
    return ok(services.listar_maquinas(musculo))


@bp.get("/<maquina_id>")
@requiere_auth
def detalle(maquina_id: str):
    return ok(services.obtener_maquina(maquina_id))