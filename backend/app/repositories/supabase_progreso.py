"""
Implementación del repositorio de progreso contra Supabase.
"""
from datetime import datetime
from typing import List, Optional
from app.domain.models import RegistroSerie
from app.repositories.progreso_repository import ProgresoRepository
from app.extensions import get_supabase


_COLUMNS = (
    "id,alumno_id,fecha,ejercicio_tipo,maquina_id,nombre_libre,rutina_id,"
    "numero_serie,peso,repeticiones,gimnasio_id"
)


def _row_a_registro(row: dict) -> RegistroSerie:
    fecha = row.get("fecha")
    return RegistroSerie(
        id=row["id"],
        alumno_id=row["alumno_id"],
        fecha=fecha.isoformat() if hasattr(fecha, "isoformat") else (fecha or ""),
        ejercicio_tipo=row["ejercicio_tipo"],
        numero_serie=row["numero_serie"],
        peso=row["peso"],
        repeticiones=row["repeticiones"],
        maquina_id=row.get("maquina_id"),
        nombre_libre=row.get("nombre_libre"),
        rutina_id=row.get("rutina_id"),
        gimnasio_id=row["gimnasio_id"],
    )


class SupabaseProgresoRepository(ProgresoRepository):

    def __init__(self):
        self._sb = get_supabase()

    # -------- Lectura --------

    def listar_por_alumno(self, alumno_id: str) -> List[RegistroSerie]:
        resp = (
            self._sb.table("progreso_registros")
            .select(_COLUMNS)
            .eq("alumno_id", alumno_id)
            .order("fecha", desc=False)
            .execute()
        )
        return [_row_a_registro(row) for row in (resp.data or [])]

    def listar_por_ejercicio(self, alumno_id: str, ejercicio_key: str) -> List[RegistroSerie]:
        key = ejercicio_key.strip().lower()
        # La clave puede ser un maquina_id (uuid) o un nombre_libre (texto).
        # Hacemos dos queries y combinamos — pero si la key parece UUID, solo la primera.
        resultados: List[RegistroSerie] = []

        # Intento como maquina_id (solo si parece UUID válido)
        if self._parece_uuid(key):
            resp = (
                self._sb.table("progreso_registros")
                .select(_COLUMNS)
                .eq("alumno_id", alumno_id)
                .eq("ejercicio_tipo", "maquina")
                .eq("maquina_id", key)
                .order("fecha")
                .execute()
            )
            resultados.extend(_row_a_registro(row) for row in (resp.data or []))
            return resultados

        # Si no es UUID, buscar por nombre_libre exacto (case-insensitive)
        # PostgREST no soporta ilike sin comodines directamente en eq;
        # usamos ilike sin % para simular case-insensitive exact.
        resp = (
            self._sb.table("progreso_registros")
            .select(_COLUMNS)
            .eq("alumno_id", alumno_id)
            .eq("ejercicio_tipo", "libre")
            .ilike("nombre_libre", key)
            .order("fecha")
            .execute()
        )
        resultados.extend(_row_a_registro(row) for row in (resp.data or []))
        return resultados

    def listar_sesion(self, alumno_id: str, ejercicio_key: str, fecha_dia: str) -> List[RegistroSerie]:
        key = ejercicio_key.strip().lower()
        # Filtro de día: comparamos los primeros 10 chars de fecha (YYYY-MM-DD)
        # PostgREST soporta gte/lte sobre timestamptz
        inicio_dia = f"{fecha_dia}T00:00:00+00:00"
        fin_dia = f"{fecha_dia}T23:59:59.999999+00:00"

        query = (
            self._sb.table("progreso_registros")
            .select(_COLUMNS)
            .eq("alumno_id", alumno_id)
            .gte("fecha", inicio_dia)
            .lte("fecha", fin_dia)
        )

        if self._parece_uuid(key):
            query = query.eq("ejercicio_tipo", "maquina").eq("maquina_id", key)
        else:
            query = query.eq("ejercicio_tipo", "libre").ilike("nombre_libre", key)

        resp = query.order("numero_serie").execute()
        return [_row_a_registro(row) for row in (resp.data or [])]

    def find_by_id(self, registro_id: str) -> Optional[RegistroSerie]:
        resp = (
            self._sb.table("progreso_registros")
            .select(_COLUMNS)
            .eq("id", registro_id)
            .limit(1)
            .execute()
        )
        if not resp.data:
            return None
        return _row_a_registro(resp.data[0])

    def siguiente_numero_serie(self, alumno_id: str, ejercicio_key: str, fecha_iso_dia: str) -> int:
        series = self.listar_sesion(alumno_id, ejercicio_key, fecha_iso_dia)
        if not series:
            return 1
        return max(s.numero_serie for s in series) + 1

    # -------- Escritura --------

    def crear(self, registro: RegistroSerie) -> RegistroSerie:
        payload = {
            "alumno_id": registro.alumno_id,
            "fecha": registro.fecha or datetime.utcnow().isoformat() + "Z",
            "ejercicio_tipo": registro.ejercicio_tipo,
            "maquina_id": registro.maquina_id if registro.ejercicio_tipo == "maquina" else None,
            "nombre_libre": registro.nombre_libre if registro.ejercicio_tipo == "libre" else None,
            "rutina_id": registro.rutina_id,
            "gimnasio_id": registro.gimnasio_id,
            "numero_serie": registro.numero_serie,
            "peso": registro.peso,
            "repeticiones": registro.repeticiones,
        }
        resp = self._sb.table("progreso_registros").insert(payload).execute()
        if not resp.data:
            raise RuntimeError("No se pudo crear el registro de progreso.")
        return _row_a_registro(resp.data[0])

    def actualizar(
        self,
        registro_id: str,
        alumno_id: str,
        peso: str,
        repeticiones: str,
    ) -> Optional[RegistroSerie]:
        # Verificamos pertenencia
        resp = (
            self._sb.table("progreso_registros")
            .select("id,alumno_id")
            .eq("id", registro_id)
            .limit(1)
            .execute()
        )
        if not resp.data or resp.data[0]["alumno_id"] != alumno_id:
            return None

        update_resp = (
            self._sb.table("progreso_registros")
            .update({"peso": peso, "repeticiones": repeticiones})
            .eq("id", registro_id)
            .execute()
        )
        if not update_resp.data:
            return None
        return _row_a_registro(update_resp.data[0])

    # -------- Helpers --------

    @staticmethod
    def _parece_uuid(valor: str) -> bool:
        """Chequeo básico de UUID v4. Evita mandar al backend algo que no es UUID."""
        if len(valor) != 36:
            return False
        partes = valor.split("-")
        return len(partes) == 5 and all(
            len(p) == n for p, n in zip(partes, [8, 4, 4, 4, 12])
        )