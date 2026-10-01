from flask import Blueprint, g, request

from app.utils.responses import ok, created
from app.utils.security.decorators import requiere_rol, requiere_auth
from app.blueprints.profesor.schemas import (
    validar_crear_solicitud_payload,
    validar_rechazo_payload,
    validar_crear_reporte_payload,
    validar_resolver_payload,
    validar_crear_solicitud_rutina_payload,
    validar_resolver_solicitud_rutina_payload,
    validar_crear_rutina_payload,
    validar_editar_rutina_payload,
    validar_duplicar_rutina_payload,
    validar_editar_datos_alumno_payload,
)
from app.blueprints.profesor import services

bp = Blueprint("profesor", __name__)


# -------- Dashboard --------

@bp.get("/dashboard")
@requiere_rol("profesor", "gimnasio")
def dashboard():
    return ok(services.obtener_dashboard())


# -------- Alumnos --------

@bp.get("/alumnos")
@requiere_rol("profesor", "gimnasio")
def listar_alumnos():
    return ok(services.listar_alumnos())


@bp.get("/alumnos/<alumno_id>/perfil")
@requiere_rol("profesor", "gimnasio")
def perfil_alumno(alumno_id: str):
    return ok(services.obtener_perfil_alumno(alumno_id, g.usuario_actual.rol))


@bp.patch("/alumnos/<alumno_id>/perfil")
@requiere_rol("profesor", "gimnasio")
def editar_perfil_alumno(alumno_id: str):
    data = request.get_json(silent=True) or {}
    payload = validar_editar_datos_alumno_payload(data)
    return ok(services.editar_datos_alumno(g.usuario_actual, alumno_id, payload))


@bp.get("/alumnos/<alumno_id>/progreso")
@requiere_rol("profesor", "gimnasio")
def progreso_alumno(alumno_id: str):
    return ok(services.obtener_progreso_alumno(alumno_id))


# -------- Profesores disponibles (para que el alumno elija) --------

@bp.get("/profesores-disponibles")
@requiere_auth
def profesores_disponibles():
    return ok(services.listar_profesores_disponibles())


# -------- Solicitudes de ejercicio --------

@bp.post("/solicitudes")
@requiere_rol("profesor", "gimnasio")
def crear_solicitud():
    data = request.get_json(silent=True) or {}
    payload = validar_crear_solicitud_payload(data)
    return created(services.crear_solicitud(g.usuario_actual, payload))


@bp.get("/solicitudes/mias")
@requiere_rol("profesor", "gimnasio")
def mis_solicitudes():
    return ok(services.listar_mis_solicitudes(g.usuario_actual.id))


@bp.post("/solicitudes/<solicitud_id>/cancelar")
@requiere_rol("profesor", "gimnasio")
def cancelar_solicitud(solicitud_id: str):
    return ok(services.cancelar_solicitud(g.usuario_actual.id, solicitud_id))


# -------- Reportes --------

@bp.post("/reportes")
@requiere_rol("profesor", "gimnasio")
def crear_reporte():
    data = request.get_json(silent=True) or {}
    payload = validar_crear_reporte_payload(data)
    return created(services.crear_reporte(g.usuario_actual, payload))


@bp.get("/reportes/mios")
@requiere_rol("profesor", "gimnasio")
def mis_reportes():
    return ok(services.listar_mis_reportes(g.usuario_actual.id))


@bp.post("/reportes/<reporte_id>/cancelar")
@requiere_rol("profesor", "gimnasio")
def cancelar_reporte(reporte_id: str):
    return ok(services.cancelar_reporte(g.usuario_actual.id, reporte_id))


# -------- Rutinas (builder del profesor) --------

@bp.get("/rutinas")
@requiere_rol("profesor", "gimnasio")
def listar_rutinas():
    incluir_inactivas = request.args.get("incluir_inactivas", "false").lower() == "true"
    return ok(services.listar_rutinas_del_profesor(g.usuario_actual.id, incluir_inactivas))


@bp.post("/rutinas")
@requiere_rol("profesor", "gimnasio")
def crear_rutina():
    data = request.get_json(silent=True) or {}
    payload = validar_crear_rutina_payload(data)
    return created(services.crear_rutina(g.usuario_actual, payload))


@bp.get("/rutinas/<rutina_id>")
@requiere_rol("profesor", "gimnasio")
def detalle_rutina(rutina_id: str):
    return ok(services.obtener_rutina_para_profesor(rutina_id))


@bp.put("/rutinas/<rutina_id>")
@requiere_rol("profesor", "gimnasio")
def editar_rutina(rutina_id: str):
    data = request.get_json(silent=True) or {}
    payload = validar_editar_rutina_payload(data)
    return ok(services.editar_rutina(g.usuario_actual, rutina_id, payload))


@bp.patch("/rutinas/<rutina_id>/archivar")
@requiere_rol("profesor", "gimnasio")
def archivar_rutina(rutina_id: str):
    return ok(services.archivar_rutina(g.usuario_actual, rutina_id))


@bp.patch("/rutinas/<rutina_id>/reactivar")
@requiere_rol("profesor", "gimnasio")
def reactivar_rutina(rutina_id: str):
    return ok(services.reactivar_rutina(g.usuario_actual, rutina_id))


@bp.post("/rutinas/<rutina_id>/duplicar")
@requiere_rol("profesor", "gimnasio")
def duplicar_rutina(rutina_id: str):
    data = request.get_json(silent=True) or {}
    payload = validar_duplicar_rutina_payload(data)
    return created(services.duplicar_rutina(g.usuario_actual, rutina_id, payload["nuevo_alumno_id"]))


@bp.get("/alumnos/<alumno_id>/rutinas")
@requiere_rol("profesor", "gimnasio")
def rutinas_de_alumno(alumno_id: str):
    incluir_inactivas = request.args.get("incluir_inactivas", "false").lower() == "true"
    return ok(services.listar_rutinas_de_alumno(alumno_id, incluir_inactivas))


# -------- Solicitudes de rutina (alumno) --------

@bp.post("/solicitudes-rutina")
@requiere_auth
def crear_solicitud_rutina():
    data = request.get_json(silent=True) or {}
    payload = validar_crear_solicitud_rutina_payload(data)
    return created(services.crear_solicitud_rutina(g.usuario_actual, payload))


@bp.get("/solicitudes-rutina/mias")
@requiere_auth
def mis_solicitudes_rutina():
    return ok(services.listar_mis_solicitudes_rutina(g.usuario_actual.id))


@bp.post("/solicitudes-rutina/<solicitud_id>/cancelar")
@requiere_auth
def cancelar_solicitud_rutina(solicitud_id: str):
    return ok(services.cancelar_solicitud_rutina(g.usuario_actual.id, solicitud_id))


# -------- Solicitudes de rutina (profesor) --------

@bp.get("/solicitudes-rutina/disponibles")
@requiere_rol("profesor", "gimnasio")
def solicitudes_rutina_disponibles():
    return ok(services.listar_solicitudes_rutina_disponibles(g.usuario_actual))


@bp.get("/solicitudes-rutina/tomadas")
@requiere_rol("profesor", "gimnasio")
def solicitudes_rutina_tomadas():
    return ok(services.listar_mis_solicitudes_rutina_como_profesor(g.usuario_actual.id))


@bp.post("/solicitudes-rutina/<solicitud_id>/tomar")
@requiere_rol("profesor", "gimnasio")
def tomar_solicitud_rutina(solicitud_id: str):
    return ok(services.tomar_solicitud_rutina(g.usuario_actual, solicitud_id))


@bp.post("/solicitudes-rutina/<solicitud_id>/resolver")
@requiere_rol("profesor", "gimnasio")
def resolver_solicitud_rutina(solicitud_id: str):
    data = request.get_json(silent=True) or {}
    payload = validar_resolver_solicitud_rutina_payload(data)
    return ok(services.resolver_solicitud_rutina(
        g.usuario_actual, solicitud_id,
        payload["mensaje_resolucion"], payload.get("rutina_id"),
    ))


@bp.post("/solicitudes-rutina/<solicitud_id>/rechazar")
@requiere_rol("profesor", "gimnasio")
def rechazar_solicitud_rutina(solicitud_id: str):
    data = request.get_json(silent=True) or {}
    payload = validar_rechazo_payload(data)
    return ok(services.rechazar_solicitud_rutina(g.usuario_actual, solicitud_id, payload["motivo"]))


@bp.post("/solicitudes-rutina/<solicitud_id>/solicitar-liberacion")
@requiere_rol("profesor", "gimnasio")
def solicitar_liberacion(solicitud_id: str):
    return ok(services.solicitar_liberacion(g.usuario_actual, solicitud_id))


# -------- Admin: solicitudes de ejercicio --------

@bp.get("/admin/pendientes/count")
@requiere_rol("gimnasio")
def count_pendientes():
    return ok(services.contar_pendientes())


@bp.get("/admin/pendientes")
@requiere_rol("gimnasio")
def listar_pendientes():
    return ok(services.listar_pendientes())


@bp.post("/admin/solicitudes/<solicitud_id>/aprobar")
@requiere_rol("gimnasio")
def aprobar_solicitud(solicitud_id: str):
    return ok(services.aprobar_solicitud(g.usuario_actual, solicitud_id))


@bp.post("/admin/solicitudes/<solicitud_id>/rechazar")
@requiere_rol("gimnasio")
def rechazar_solicitud(solicitud_id: str):
    data = request.get_json(silent=True) or {}
    payload = validar_rechazo_payload(data)
    return ok(services.rechazar_solicitud(g.usuario_actual, solicitud_id, payload["motivo"]))


# -------- Admin: reportes --------

@bp.get("/admin/reportes/count")
@requiere_rol("gimnasio")
def count_reportes():
    return ok(services.contar_reportes())


@bp.get("/admin/reportes")
@requiere_rol("gimnasio")
def listar_reportes():
    return ok(services.listar_todos_reportes())


@bp.post("/admin/reportes/<reporte_id>/en-revision")
@requiere_rol("gimnasio")
def en_revision_reporte(reporte_id: str):
    return ok(services.marcar_reporte_en_revision(g.usuario_actual, reporte_id))


@bp.post("/admin/reportes/<reporte_id>/resolver")
@requiere_rol("gimnasio")
def resolver_reporte(reporte_id: str):
    data = request.get_json(silent=True) or {}
    payload = validar_resolver_payload(data)
    return ok(services.resolver_reporte(g.usuario_actual, reporte_id, payload["resolucion"]))


# -------- Admin: liberaciones de solicitudes de rutina --------

@bp.get("/admin/solicitudes-rutina/liberaciones")
@requiere_rol("gimnasio")
def liberaciones_pendientes():
    return ok(services.listar_liberaciones_pendientes())


@bp.post("/admin/solicitudes-rutina/<solicitud_id>/liberar/aprobar")
@requiere_rol("gimnasio")
def aprobar_liberacion(solicitud_id: str):
    return ok(services.aprobar_liberacion(g.usuario_actual, solicitud_id))


@bp.post("/admin/solicitudes-rutina/<solicitud_id>/liberar/rechazar")
@requiere_rol("gimnasio")
def rechazar_liberacion(solicitud_id: str):
    data = request.get_json(silent=True) or {}
    payload = validar_rechazo_payload(data)
    return ok(services.rechazar_liberacion(g.usuario_actual, solicitud_id, payload["motivo"]))


@bp.get("/admin/solicitudes-rutina")
@requiere_rol("gimnasio")
def listar_todas_solicitudes_rutina():
    return ok(services.listar_todas_solicitudes_rutina())

@bp.get("/alumnos/<alumno_id>/solicitudes-rutina")
@requiere_rol("profesor", "gimnasio")
def solicitudes_rutina_de_alumno(alumno_id: str):
    return ok(services.listar_solicitudes_rutina_de_alumno(alumno_id))

@bp.get("/mis-horarios")
@requiere_rol("profesor", "gimnasio")
def mis_horarios():
    return ok(services.listar_mis_horarios(g.usuario_actual.id))