"""
Interfaz del repositorio de reportes.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import Reporte


class ReportesRepository(ABC):

    @abstractmethod
    def crear(self, reporte: Reporte) -> Reporte:
        ...

    @abstractmethod
    def find_by_id(self, reporte_id: str) -> Optional[Reporte]:
        ...

    @abstractmethod
    def listar_por_reportante(self, reportante_id: str) -> List[Reporte]:
        ...

    @abstractmethod
    def listar_todos(self) -> List[Reporte]:
        ...
        
    @abstractmethod
    def actualizar(self, reporte_id: str, data: dict) -> Optional[Reporte]:
        ...