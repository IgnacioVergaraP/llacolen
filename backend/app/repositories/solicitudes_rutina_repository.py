"""
Interfaz del repositorio de solicitudes de rutina.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import SolicitudRutina


class SolicitudesRutinaRepository(ABC):

    @abstractmethod
    def crear(self, solicitud: SolicitudRutina) -> SolicitudRutina:
        ...

    @abstractmethod
    def find_by_id(self, solicitud_id: str) -> Optional[SolicitudRutina]:
        ...

    @abstractmethod
    def listar_por_alumno(self, alumno_id: str) -> List[SolicitudRutina]:
        ...

    @abstractmethod
    def listar_todas(self, gimnasio_id: str) -> List[SolicitudRutina]:
        ...

    @abstractmethod
    def listar_pendientes(self, gimnasio_id: str) -> List[SolicitudRutina]:
        ...

    @abstractmethod
    def listar_por_profesor(self, profesor_id: str) -> List[SolicitudRutina]:
        ...

    @abstractmethod
    def actualizar(self, solicitud_id: str, data: dict) -> Optional[SolicitudRutina]:
        ...