"""
Implementación mock del repositorio de máquinas.
"""
from typing import List, Optional
from app.domain.models import Maquina
from app.repositories.maquinas_repository import MaquinasRepository


_MAQUINAS_MOCK: List[Maquina] = [
    Maquina(id="mq-001", nombre="Press de banca", grupos_musculares=["pecho", "triceps", "hombros"],
            descripcion="Ejercicio compuesto para el desarrollo del pectoral mayor, con participación secundaria de tríceps y deltoides anterior.",
            video_url="https://www.youtube.com/embed/rT7DgCr-3pg", imagen_url=""),
    Maquina(id="mq-002", nombre="Press inclinado con mancuernas", grupos_musculares=["pecho", "hombros"],
            descripcion="Variante del press que enfatiza la porción clavicular del pectoral. Banco inclinado a 30-45°.",
            video_url="https://www.youtube.com/embed/8iPEnn-ltC8", imagen_url=""),
    Maquina(id="mq-003", nombre="Remo con barra", grupos_musculares=["espalda", "biceps"],
            descripcion="Ejercicio compuesto para el desarrollo de la espalda media y dorsal ancho.",
            video_url="https://www.youtube.com/embed/9efgcAjQe7E", imagen_url=""),
    Maquina(id="mq-004", nombre="Jalón al pecho en polea", grupos_musculares=["espalda", "biceps"],
            descripcion="Ejercicio de tracción vertical para dorsal ancho.",
            video_url="https://www.youtube.com/embed/CAwf7n6Luuc", imagen_url=""),
    Maquina(id="mq-005", nombre="Sentadilla con barra", grupos_musculares=["piernas", "core"],
            descripcion="El ejercicio rey para el tren inferior. Cuádriceps, isquiotibiales, glúteos y core.",
            video_url="https://www.youtube.com/embed/ultWZbUMPL8", imagen_url=""),
    Maquina(id="mq-006", nombre="Prensa de piernas 45°", grupos_musculares=["piernas"],
            descripcion="Ejercicio guiado en máquina para cuádriceps, isquiotibiales y glúteos.",
            video_url="https://www.youtube.com/embed/IZxyjW7MPJQ", imagen_url=""),
    Maquina(id="mq-007", nombre="Peso muerto rumano", grupos_musculares=["piernas", "espalda"],
            descripcion="Bisagra de cadera que enfatiza isquiotibiales y glúteos.",
            video_url="https://www.youtube.com/embed/2SHsk9AzdjA", imagen_url=""),
    Maquina(id="mq-008", nombre="Press militar con barra", grupos_musculares=["hombros", "triceps"],
            descripcion="Ejercicio compuesto para deltoides.",
            video_url="https://www.youtube.com/embed/2yjwXTZQDDI", imagen_url=""),
    Maquina(id="mq-009", nombre="Curl de bíceps con mancuernas", grupos_musculares=["biceps"],
            descripcion="Ejercicio de aislamiento para bíceps braquial.",
            video_url="https://www.youtube.com/embed/ykJmrZ5v0Oo", imagen_url=""),
    Maquina(id="mq-010", nombre="Plancha abdominal", grupos_musculares=["core"],
            descripcion="Ejercicio isométrico para core.",
            video_url="https://www.youtube.com/embed/pSHjTRCQxIw", imagen_url=""),
]


class MockMaquinasRepository(MaquinasRepository):

    def __init__(self):
        # Lista compartida a nivel módulo: los cambios persisten entre instancias.
        self._maquinas: List[Maquina] = _MAQUINAS_MOCK

    def _calcular_next_num(self) -> int:
        max_n = 0
        for m in self._maquinas:
            try:
                n = int(m.id.replace("mq-", ""))
                if n > max_n:
                    max_n = n
            except ValueError:
                continue
        return max_n + 1

    def listar(self) -> List[Maquina]:
        return list(self._maquinas)

    def listar_por_musculo(self, musculo: str) -> List[Maquina]:
        musculo = musculo.strip().lower()
        return [
            m for m in self._maquinas
            if musculo in [g.lower() for g in m.grupos_musculares]
        ]

    def find_by_id(self, maquina_id: str) -> Optional[Maquina]:
        for m in self._maquinas:
            if m.id == maquina_id:
                return m
        return None

    def crear(
        self,
        nombre: str,
        grupos_musculares: List[str],
        descripcion: str,
        video_url: str,
        imagen_url: str = "",
    ) -> Maquina:
        nuevo_id = f"mq-{self._calcular_next_num():03d}"
        maquina = Maquina(
            id=nuevo_id,
            nombre=nombre,
            grupos_musculares=list(grupos_musculares),
            descripcion=descripcion,
            video_url=video_url,
            imagen_url=imagen_url,
        )
        self._maquinas.append(maquina)
        return maquina