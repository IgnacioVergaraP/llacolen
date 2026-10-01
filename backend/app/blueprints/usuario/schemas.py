"""Validación del módulo usuario."""
from datetime import date
from app.errors import AuthError


_CAMPOS_PROHIBIDOS = (
    "id",
    "email",
    "rol",
    "password_hash",
    "activo",
    "fecha_alta",
    "imc",
    "origen_grasa",
    "cargado_por_id",
)


def validar_actualizar_perfil_payload(data: dict) -> dict:
    if not isinstance(data, dict):
        raise AuthError(400, "InvalidPayload", "Se esperaba un objeto JSON.")

    out = {}

    # --- nombre ---
    if "nombre" in data:
        nombre = data.get("nombre")
        if not isinstance(nombre, str):
            raise AuthError(400, "InvalidPayload", "'nombre' debe ser texto.")
        nombre = nombre.strip()
        if len(nombre) < 2:
            raise AuthError(400, "InvalidName", "El nombre debe tener al menos 2 caracteres.")
        if len(nombre) > 80:
            raise AuthError(400, "InvalidName", "El nombre no puede superar los 80 caracteres.")
        out["nombre"] = nombre

    # --- altura ---
    if "altura" in data:
        altura = data.get("altura")
        if altura is not None:
            if not isinstance(altura, (int, float)):
                raise AuthError(400, "InvalidPayload", "'altura' debe ser numérico o null.")
            if altura < 50 or altura > 250:
                raise AuthError(400, "InvalidAltura", "La altura debe estar entre 50 y 250 cm.")
            out["altura"] = float(altura)

    # --- peso_actual ---
    if "peso_actual" in data:
        peso = data.get("peso_actual")
        if peso is not None:
            if not isinstance(peso, (int, float)):
                raise AuthError(400, "InvalidPayload", "'peso_actual' debe ser numérico o null.")
            if peso < 20 or peso > 300:
                raise AuthError(400, "InvalidPeso", "El peso debe estar entre 20 y 300 kg.")
            out["peso_actual"] = float(peso)

    # --- peso_objetivo ---
    if "peso_objetivo" in data:
        peso_obj = data.get("peso_objetivo")
        if peso_obj is not None:
            if not isinstance(peso_obj, (int, float)):
                raise AuthError(400, "InvalidPayload", "'peso_objetivo' debe ser numérico o null.")
            if peso_obj < 20 or peso_obj > 300:
                raise AuthError(400, "InvalidPesoObjetivo", "El peso objetivo debe estar entre 20 y 300 kg.")
            out["peso_objetivo"] = float(peso_obj)

    # --- imagen_url ---
    if "imagen_url" in data:
        url = data.get("imagen_url")
        if url is not None:
            if not isinstance(url, str):
                raise AuthError(400, "InvalidPayload", "'imagen_url' debe ser texto o null.")
            url = url.strip()
            if url and len(url) > 500:
                raise AuthError(400, "InvalidImageUrl", "La URL de imagen es demasiado larga.")
            if url and not (url.startswith("http://") or url.startswith("https://")):
                raise AuthError(400, "InvalidImageUrl", "La URL debe empezar con http:// o https://.")
            out["imagen_url"] = url or None

    # --- porcentaje_grasa ---
    if "porcentaje_grasa" in data:
        pg = data.get("porcentaje_grasa")
        if pg is not None:
            if not isinstance(pg, (int, float)):
                raise AuthError(400, "InvalidPayload", "'porcentaje_grasa' debe ser numérico o null.")
            if pg < 3 or pg > 70:
                raise AuthError(400, "InvalidGrasa", "El porcentaje de grasa debe estar entre 3 y 70.")
            out["porcentaje_grasa"] = float(pg)

    # --- fecha_medicion_grasa ---
    if "fecha_medicion_grasa" in data:
        fecha = data.get("fecha_medicion_grasa")
        if fecha is not None:
            if not isinstance(fecha, str):
                raise AuthError(400, "InvalidPayload", "'fecha_medicion_grasa' debe ser texto o null.")
            fecha = fecha.strip()
            try:
                date.fromisoformat(fecha)
            except ValueError:
                raise AuthError(400, "InvalidFecha", "La fecha debe tener formato YYYY-MM-DD.")
            out["fecha_medicion_grasa"] = fecha

    # --- bio ---
    if "bio" in data:
        bio = data.get("bio")
        if bio is not None:
            if not isinstance(bio, str):
                raise AuthError(400, "InvalidPayload", "'bio' debe ser texto o null.")
            bio = bio.strip()
            if len(bio) > 500:
                raise AuthError(400, "InvalidBio", "La bio no puede superar los 500 caracteres.")
            out["bio"] = bio or None

    # --- especialidades ---
    if "especialidades" in data:
        esp = data.get("especialidades")
        if esp is not None:
            if not isinstance(esp, list):
                raise AuthError(400, "InvalidPayload", "'especialidades' debe ser una lista o null.")
            if len(esp) > 6:
                raise AuthError(400, "InvalidEspecialidades", "Máximo 6 especialidades.")
            limpio = []
            for item in esp:
                if not isinstance(item, str):
                    raise AuthError(400, "InvalidEspecialidades", "Cada especialidad debe ser texto.")
                item = item.strip().lower()
                if len(item) < 2 or len(item) > 40:
                    raise AuthError(400, "InvalidEspecialidades", "Cada especialidad debe tener entre 2 y 40 caracteres.")
                if item:
                    limpio.append(item)
            out["especialidades"] = limpio or None

    # --- anios_experiencia ---
    if "anios_experiencia" in data:
        anios = data.get("anios_experiencia")
        if anios is not None:
            if not isinstance(anios, int):
                raise AuthError(400, "InvalidPayload", "'anios_experiencia' debe ser entero o null.")
            if anios < 0 or anios > 60:
                raise AuthError(400, "InvalidAnios", "Los años de experiencia deben estar entre 0 y 60.")
            out["anios_experiencia"] = anios

    # --- telefono ---
    if "telefono" in data:
        tel = data.get("telefono")
        if tel is not None:
            if not isinstance(tel, str):
                raise AuthError(400, "InvalidPayload", "'telefono' debe ser texto o null.")
            tel = tel.strip()
            if tel and (len(tel) < 6 or len(tel) > 20):
                raise AuthError(400, "InvalidTelefono", "El teléfono debe tener entre 6 y 20 caracteres.")
            out["telefono"] = tel or None

    # --- campos prohibidos ---
    for campo in _CAMPOS_PROHIBIDOS:
        if campo in data:
            raise AuthError(
                400,
                "ForbiddenField",
                f"El campo '{campo}' no se puede modificar desde este endpoint.",
            )

    if not out:
        raise AuthError(400, "EmptyPayload", "No se envió ningún campo para actualizar.")

    return out