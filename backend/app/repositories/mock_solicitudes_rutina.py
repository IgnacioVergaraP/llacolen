"""
Implementación mock del repositorio de solicitudes de rutina.
"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from app.domain.models import SolicitudRutina
from app.repositories.solicitudes_rutina_repository import SolicitudesRutinaRepository


def _ahora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hace_dias(dias: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=dias)
    return dt.isoformat()


# Datos de ejemplo
_SOLICITUDES_INICIALES: List[SolicitudRutina] = [
    # María pide una rutina específica al Prof. Martínez
    SolicitudRutina(
        id="srt-0001",
        estado="pendiente",
        alumno_id="u-alu-002",
        alumno_nombre="María González",
        objetivo="hipertrofia",
        dias_por_semana=4,
        comentarios="Quiero enfocarme en tren inferior. Tengo molestia en el hombro derecho.",
        grupos_interes=["piernas", "core"],
        profesor_preferido_id="u-pro-001",
        profesor_preferido_nombre="Prof. Martínez",
        fecha_creacion=_hace_dias(1),
    ),
    # Lucía pide una rutina en pool general (sin profesor preferido)
    SolicitudRutina(
        id="srt-0002",
        estado="pendiente",
        alumno_id="u-alu-004",
        alumno_nombre="Lucía Fernández",
        objetivo="mantenimiento",
        dias_por_semana=3,
        comentarios="Vuelvo después de un parate largo. Prefiero arrancar suave.",
        grupos_interes=[],
        fecha_creacion=_hace_dias(2),
    ),
]


class MockSolicitudesRutinaRepository(SolicitudesRutinaRepository):

    def __init__(self):
        # Lista compartida a nivel módulo: los cambios persisten entre instancias.
        self._solicitudes: List[SolicitudRutina] = _SOLICITUDES_INICIALES

    def _calcular_next_num(self) -> int:
        max_n = 0
        for s in self._solicitudes:
            try:
                n = int(s.id.replace("srt-", ""))
                if n > max_n:
                    max_n = n
            except ValueError:
                continue
        return max_n + 1

    def _generar_id(self) -> str:
        return f"srt-{self._calcular_next_num():04d}"

    def crear(self, solicitud: SolicitudRutina) -> SolicitudRutina:
        solicitud.id = self._generar_id()
        solicitud.fecha_creacion = _ahora_iso()
        self._solicitudes.append(solicitud)
        return solicitud

    def find_by_id(self, solicitud_id: str) -> Optional[SolicitudRutina]:
        for s in self._solicitudes:
            if s.id == solicitud_id:
                return s
        return None

    def listar_por_alumno(self, alumno_id: str) -> List[SolicitudRutina]:
        result = [s for s in self._solicitudes if s.alumno_id == alumno_id]
        result.sort(key=lambda s: s.fecha_creacion, reverse=True)
        return result

    def listar_todas(self) -> List[SolicitudRutina]:
        result = list(self._solicitudes)
        result.sort(key=lambda s: s.fecha_creacion, reverse=True)
        return result

    def listar_pendientes(self) -> List[SolicitudRutina]:
        result = [s for s in self._solicitudes if s.estado == "pendiente"]
        result.sort(key=lambda s: s.fecha_creacion)
        return result

    def listar_por_profesor(self, profesor_id: str) -> List[SolicitudRutina]:
        result = [s for s in self._solicitudes if s.profesor_id == profesor_id]
        result.sort(key=lambda s: s.fecha_creacion, reverse=True)
        return result
    
    def actualizar(self, solicitud_id: str, data: dict) -> Optional[SolicitudRutina]:
        solicitud = self.find_by_id(solicitud_id)
        if not solicitud:
            return None
        for key, value in data.items():
            if hasattr(solicitud, key):
                setattr(solicitud, key, value)
        return solicitud