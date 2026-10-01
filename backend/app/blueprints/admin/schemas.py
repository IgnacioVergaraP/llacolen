"""Validación del módulo admin."""
import re
from app.errors import AuthError
from datetime import date


_HORA_REGEX = re.compile(r"^\d{2}:\d{2}$")
TIPOS_MANTENIMIENTO = ("preventivo", "correctivo", "limpieza", "revision")


def _minutos(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _validar_hora(valor, campo: str) -> str:
    if not isinstance(valor, str) or not _HORA_REGEX.match(valor.strip()):
        raise AuthError(400, "InvalidHora", f"'{campo}' debe tener formato HH:MM.")
    valor = valor.strip()
    h, m = valor.split(":")
    if int(h) < 0 or int(h) > 23 or int(m) < 0 or int(m) > 59:
        raise AuthError(400, "InvalidHora", f"'{campo}' fuera de rango.")
    return valor


def _validar_dia(valor) -> int:
    if not isinstance(valor, int) or valor < 0 or valor > 6:
        raise AuthError(400, "InvalidDia", "'dia_semana' debe ser un entero entre 0 (lunes) y 6 (domingo).")
    return valor


def validar_crear_horario_payload(data: dict) -> dict:
    if not isinstance(data, dict):
        raise AuthError(400, "InvalidPayload", "Se esperaba un objeto JSON.")

    profesor_id = data.get("profesor_id")
    if not isinstance(profesor_id, str) or not profesor_id.strip():
        raise AuthError(400, "InvalidPayload", "'profesor_id' es obligatorio.")
    profesor_id = profesor_id.strip()

    dia = _validar_dia(data.get("dia_semana"))
    hora_inicio = _validar_hora(data.get("hora_inicio"), "hora_inicio")
    hora_fin = _validar_hora(data.get("hora_fin"), "hora_fin")

    if _minutos(hora_inicio) >= _minutos(hora_fin):
        raise AuthError(400, "InvalidRango", "'hora_inicio' debe ser menor que 'hora_fin'.")

    notas = data.get("notas")
    if notas is not None:
        if not isinstance(notas, str):
            raise AuthError(400, "InvalidPayload", "'notas' debe ser texto o null.")
        notas = notas.strip() or None
        if notas and len(notas) > 200:
            raise AuthError(400, "InvalidNotas", "Las notas no pueden superar los 200 caracteres.")

    return {
        "profesor_id": profesor_id,
        "dia_semana": dia,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "notas": notas,
    }


def validar_editar_horario_payload(data: dict) -> dict:
    if not isinstance(data, dict):
        raise AuthError(400, "InvalidPayload", "Se esperaba un objeto JSON.")

    out = {}

    if "dia_semana" in data:
        out["dia_semana"] = _validar_dia(data.get("dia_semana"))

    if "hora_inicio" in data:
        out["hora_inicio"] = _validar_hora(data.get("hora_inicio"), "hora_inicio")

    if "hora_fin" in data:
        out["hora_fin"] = _validar_hora(data.get("hora_fin"), "hora_fin")

    if "notas" in data:
        notas = data.get("notas")
        if notas is not None:
            if not isinstance(notas, str):
                raise AuthError(400, "InvalidPayload", "'notas' debe ser texto o null.")
            notas = notas.strip() or None
            if notas and len(notas) > 200:
                raise AuthError(400, "InvalidNotas", "Las notas no pueden superar los 200 caracteres.")
        out["notas"] = notas

    if not out:
        raise AuthError(400, "EmptyPayload", "No se envió ningún campo para actualizar.")

    return out


def validar_crear_mantenimiento_payload(data: dict) -> dict:
    if not isinstance(data, dict):
        raise AuthError(400, "InvalidPayload", "Se esperaba un objeto JSON.")

    maquina_id = data.get("maquina_id")
    if not isinstance(maquina_id, str) or not maquina_id.strip():
        raise AuthError(400, "InvalidPayload", "'maquina_id' es obligatorio.")
    maquina_id = maquina_id.strip()

    tipo = data.get("tipo")
    if tipo not in TIPOS_MANTENIMIENTO:
        raise AuthError(400, "InvalidTipo", f"'tipo' debe ser uno de: {', '.join(TIPOS_MANTENIMIENTO)}.")

    notas = data.get("notas")
    if notas is not None:
        if not isinstance(notas, str):
            raise AuthError(400, "InvalidPayload", "'notas' debe ser texto o null.")
        notas = notas.strip() or None
        if notas and len(notas) > 500:
            raise AuthError(400, "InvalidNotas", "Las notas no pueden superar los 500 caracteres.")

    # Fecha opcional (default: hoy). Si viene, debe ser 'YYYY-MM-DD'.
    fecha = data.get("fecha")
    if fecha is not None:
        if not isinstance(fecha, str) or not fecha.strip():
            raise AuthError(400, "InvalidPayload", "'fecha' debe ser texto o null.")
        fecha = fecha.strip()
        try:
            date.fromisoformat(fecha)
        except ValueError:
            raise AuthError(400, "InvalidFecha", "'fecha' debe tener formato YYYY-MM-DD.")
    else:
        fecha = None

    return {
        "maquina_id": maquina_id,
        "tipo": tipo,
        "notas": notas,
        "fecha": fecha,
    }