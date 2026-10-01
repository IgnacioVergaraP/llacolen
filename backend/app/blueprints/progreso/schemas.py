"""Validación del módulo progreso."""
import re
from app.errors import AuthError


def validar_crear_serie_payload(data: dict) -> dict:
    if not isinstance(data, dict):
        raise AuthError(400, "InvalidPayload", "Se esperaba un objeto JSON.")

    ejercicio_tipo = data.get("ejercicio_tipo")
    if ejercicio_tipo not in ("maquina", "libre"):
        raise AuthError(
            400, "InvalidPayload",
            "'ejercicio_tipo' debe ser 'maquina' o 'libre'."
        )

    peso = data.get("peso")
    if not isinstance(peso, str) or not peso.strip():
        raise AuthError(400, "InvalidPayload", "'peso' es obligatorio y debe ser texto.")
    peso = peso.strip()

    repeticiones = data.get("repeticiones")
    if not isinstance(repeticiones, str) or not repeticiones.strip():
        raise AuthError(400, "InvalidPayload", "'repeticiones' es obligatorio y debe ser texto.")
    repeticiones = repeticiones.strip()

    maquina_id = data.get("maquina_id")
    nombre_libre = data.get("nombre_libre")

    if ejercicio_tipo == "maquina":
        if not isinstance(maquina_id, str) or not maquina_id.strip():
            raise AuthError(
                400, "InvalidPayload",
                "'maquina_id' es obligatorio cuando ejercicio_tipo = 'maquina'."
            )
        maquina_id = maquina_id.strip()
        nombre_libre = None
    else:
        if not isinstance(nombre_libre, str) or not nombre_libre.strip():
            raise AuthError(
                400, "InvalidPayload",
                "'nombre_libre' es obligatorio cuando ejercicio_tipo = 'libre'."
            )
        nombre_libre = nombre_libre.strip()
        maquina_id = None

    rutina_id = data.get("rutina_id")
    if rutina_id is not None and (not isinstance(rutina_id, str) or not rutina_id.strip()):
        raise AuthError(400, "InvalidPayload", "'rutina_id' debe ser texto o null.")
    rutina_id = rutina_id.strip() if isinstance(rutina_id, str) else None

    numero_serie = data.get("numero_serie")
    if numero_serie is not None:
        if not isinstance(numero_serie, int) or numero_serie < 1:
            raise AuthError(400, "InvalidPayload", "'numero_serie' debe ser un entero positivo.")

    return {
        "ejercicio_tipo": ejercicio_tipo,
        "peso": peso,
        "repeticiones": repeticiones,
        "maquina_id": maquina_id,
        "nombre_libre": nombre_libre,
        "rutina_id": rutina_id,
        "numero_serie": numero_serie,
    }


def validar_actualizar_serie_payload(data: dict) -> dict:
    if not isinstance(data, dict):
        raise AuthError(400, "InvalidPayload", "Se esperaba un objeto JSON.")

    peso = data.get("peso")
    if not isinstance(peso, str) or not peso.strip():
        raise AuthError(400, "InvalidPayload", "'peso' es obligatorio y debe ser texto.")
    peso = peso.strip()

    repeticiones = data.get("repeticiones")
    if not isinstance(repeticiones, str) or not repeticiones.strip():
        raise AuthError(400, "InvalidPayload", "'repeticiones' es obligatorio y debe ser texto.")
    repeticiones = repeticiones.strip()

    return {"peso": peso, "repeticiones": repeticiones}


def validar_query_ejercicio(raw) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise AuthError(400, "InvalidQuery", "Falta el parámetro 'ejercicio'.")
    value = raw.strip()
    if len(value) > 120:
        raise AuthError(400, "InvalidQuery", "El parámetro 'ejercicio' es demasiado largo.")
    return value


def validar_query_fecha(raw) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise AuthError(400, "InvalidQuery", "Falta el parámetro 'fecha'.")
    value = raw.strip()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
        raise AuthError(400, "InvalidQuery", "El parámetro 'fecha' debe tener formato YYYY-MM-DD.")
    return value