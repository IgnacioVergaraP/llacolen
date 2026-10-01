"""
Implementación mock del repositorio de progreso.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from app.domain.models import RegistroSerie
from app.repositories.progreso_repository import ProgresoRepository


def _fecha(dias_atras: int, hora: int = 19, minuto: int = 30) -> str:
    dt = datetime.now().replace(hour=hora, minute=minuto, second=0, microsecond=0)
    dt = dt - timedelta(days=dias_atras)
    return dt.isoformat()


_REGISTROS_MOCK: List[RegistroSerie] = []


def _agregar(alumno_id, dias_atras, tipo, peso, reps, num, maquina=None, libre=None, rutina=None, hora=19, minuto=0):
    _REGISTROS_MOCK.append(
        RegistroSerie(
            id=f"rs-{len(_REGISTROS_MOCK) + 1:04d}",
            alumno_id=alumno_id,
            fecha=_fecha(dias_atras, hora, minuto),
            ejercicio_tipo=tipo,
            numero_serie=num,
            peso=peso,
            repeticiones=reps,
            maquina_id=maquina,
            nombre_libre=libre,
            rutina_id=rutina,
        )
    )


# ============ u-alu-001 — Juan Pérez ============
# Sesión de hoy: press de banca (rutina)
_agregar("u-alu-001", 0, "maquina", "60 kg", "10", 1, maquina="mq-001", rutina="rt-002", hora=19, minuto=10)
_agregar("u-alu-001", 0, "maquina", "60 kg", "9",  2, maquina="mq-001", rutina="rt-002", hora=19, minuto=14)
_agregar("u-alu-001", 0, "maquina", "60 kg", "8",  3, maquina="mq-001", rutina="rt-002", hora=19, minuto=18)
# Hace 3 días: press de banca
_agregar("u-alu-001", 3, "maquina", "57.5 kg", "10", 1, maquina="mq-001", rutina="rt-002")
_agregar("u-alu-001", 3, "maquina", "57.5 kg", "10", 2, maquina="mq-001", rutina="rt-002")
# Hace 7 días: press de banca
_agregar("u-alu-001", 7, "maquina", "55 kg", "10", 1, maquina="mq-001", rutina="rt-002")
_agregar("u-alu-001", 7, "maquina", "55 kg", "9",  2, maquina="mq-001", rutina="rt-002")
# Hace 10 días: sentadilla
_agregar("u-alu-001", 10, "maquina", "80 kg", "8", 1, maquina="mq-005")
_agregar("u-alu-001", 10, "maquina", "80 kg", "8", 2, maquina="mq-005")
_agregar("u-alu-001", 10, "maquina", "80 kg", "7", 3, maquina="mq-005")
# Hace 14 días: sentadilla
_agregar("u-alu-001", 14, "maquina", "77.5 kg", "8", 1, maquina="mq-005")
_agregar("u-alu-001", 14, "maquina", "77.5 kg", "8", 2, maquina="mq-005")
# Hace 5 días: plancha
_agregar("u-alu-001", 5, "maquina", "corporal", "45 segundos", 1, maquina="mq-010", hora=20, minuto=0)
_agregar("u-alu-001", 5, "maquina", "corporal", "50 segundos", 2, maquina="mq-010", hora=20, minuto=3)
# Hace 4 días: face pull libre
_agregar("u-alu-001", 4, "libre", "Banda media", "15", 1, libre="Face pull con banda elástica", rutina="rt-001", hora=19, minuto=30)
_agregar("u-alu-001", 4, "libre", "Banda media", "15", 2, libre="Face pull con banda elástica", rutina="rt-001", hora=19, minuto=34)

# ============ u-alu-002 — María González ============
# Hoy: sentadilla
_agregar("u-alu-002", 0, "maquina", "50 kg", "10", 1, maquina="mq-005", hora=18, minuto=0)
_agregar("u-alu-002", 0, "maquina", "50 kg", "10", 2, maquina="mq-005", hora=18, minuto=5)
# Hace 2 días: sentadilla
_agregar("u-alu-002", 2, "maquina", "47.5 kg", "10", 1, maquina="mq-005")
_agregar("u-alu-002", 2, "maquina", "47.5 kg", "10", 2, maquina="mq-005")
# Hace 5 días: curl bíceps
_agregar("u-alu-002", 5, "maquina", "8 kg por mano", "12", 1, maquina="mq-009")
_agregar("u-alu-002", 5, "maquina", "8 kg por mano", "12", 2, maquina="mq-009")

# ============ u-alu-003 — Carlos Rodríguez ============
# Hoy: press de banca
_agregar("u-alu-003", 0, "maquina", "75 kg", "8", 1, maquina="mq-001", hora=20, minuto=0)
_agregar("u-alu-003", 0, "maquina", "75 kg", "8", 2, maquina="mq-001", hora=20, minuto=5)
_agregar("u-alu-003", 0, "maquina", "75 kg", "7", 3, maquina="mq-001", hora=20, minuto=10)
# Hace 4 días: press de banca
_agregar("u-alu-003", 4, "maquina", "72.5 kg", "8", 1, maquina="mq-001")
_agregar("u-alu-003", 4, "maquina", "72.5 kg", "8", 2, maquina="mq-001")
# Hace 8 días: press inclinado
_agregar("u-alu-003", 8, "maquina", "22 kg por mano", "10", 1, maquina="mq-002")
_agregar("u-alu-003", 8, "maquina", "22 kg por mano", "9",  2, maquina="mq-002")

# ============ u-alu-004 — Lucía Fernández ============
# Hace 6 días: plancha
_agregar("u-alu-004", 6, "maquina", "corporal", "40 segundos", 1, maquina="mq-010")
_agregar("u-alu-004", 6, "maquina", "corporal", "35 segundos", 2, maquina="mq-010")


class MockProgresoRepository(ProgresoRepository):

    def __init__(self):
        # Lista compartida a nivel módulo: los cambios persisten entre instancias.
        self._registros: List[RegistroSerie] = _REGISTROS_MOCK

    def _calcular_next_num(self) -> int:
        max_n = 0
        for r in self._registros:
            try:
                n = int(r.id.replace("rs-", ""))
                if n > max_n:
                    max_n = n
            except ValueError:
                continue
        return max_n + 1

    def _generar_id(self) -> str:
        return f"rs-{self._calcular_next_num():04d}"

    def crear(self, registro: RegistroSerie) -> RegistroSerie:
        registro.id = self._generar_id()
        self._registros.append(registro)
        return registro

    def listar_por_alumno(self, alumno_id: str) -> List[RegistroSerie]:
        return [r for r in self._registros if r.alumno_id == alumno_id]

    def listar_por_ejercicio(self, alumno_id: str, ejercicio_key: str) -> List[RegistroSerie]:
        key = ejercicio_key.strip().lower()
        result = []
        for r in self._registros:
            if r.alumno_id != alumno_id:
                continue
            if r.ejercicio_tipo == "maquina" and r.maquina_id and r.maquina_id.lower() == key:
                result.append(r)
            elif r.ejercicio_tipo == "libre" and r.nombre_libre and r.nombre_libre.lower() == key:
                result.append(r)
        return result

    def listar_sesion(
        self, alumno_id: str, ejercicio_key: str, fecha_dia: str
    ) -> List[RegistroSerie]:
        key = ejercicio_key.strip().lower()
        result = []
        for r in self._registros:
            if r.alumno_id != alumno_id:
                continue
            if not r.fecha.startswith(fecha_dia):
                continue
            match = False
            if r.ejercicio_tipo == "maquina" and r.maquina_id and r.maquina_id.lower() == key:
                match = True
            elif r.ejercicio_tipo == "libre" and r.nombre_libre and r.nombre_libre.lower() == key:
                match = True
            if match:
                result.append(r)
        result.sort(key=lambda r: r.numero_serie)
        return result

    def siguiente_numero_serie(self, alumno_id: str, ejercicio_key: str, fecha_iso_dia: str) -> int:
        key = ejercicio_key.strip().lower()
        max_n = 0
        for r in self._registros:
            if r.alumno_id != alumno_id:
                continue
            if not r.fecha.startswith(fecha_iso_dia):
                continue
            match = False
            if r.ejercicio_tipo == "maquina" and r.maquina_id and r.maquina_id.lower() == key:
                match = True
            elif r.ejercicio_tipo == "libre" and r.nombre_libre and r.nombre_libre.lower() == key:
                match = True
            if match and r.numero_serie > max_n:
                max_n = r.numero_serie
        return max_n + 1

    def find_by_id(self, registro_id: str) -> Optional[RegistroSerie]:
        for r in self._registros:
            if r.id == registro_id:
                return r
        return None

    def actualizar(
        self,
        registro_id: str,
        alumno_id: str,
        peso: str,
        repeticiones: str,
    ) -> Optional[RegistroSerie]:
        registro = self.find_by_id(registro_id)
        if not registro or registro.alumno_id != alumno_id:
            return None
        registro.peso = peso
        registro.repeticiones = repeticiones
        return registro