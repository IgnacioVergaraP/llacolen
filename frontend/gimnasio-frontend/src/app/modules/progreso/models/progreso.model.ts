export type TipoEjercicio = 'maquina' | 'libre';

export interface HistorialFila {
  ejercicio: string;
  ejercicio_tipo: TipoEjercicio;
  maquina_id: string | null;
  nombre_libre: string | null;
  fecha: string;
  cantidad_series: number;
  peso_max: number | null;
  rutina_id: string | null;
}

export interface PuntoEvolucion {
  fecha: string;
  peso_max: number;
  cantidad_series: number;
}

export interface Evolucion {
  ejercicio: string;
  ejercicio_tipo: TipoEjercicio | null;
  maquina_id: string | null;
  nombre_libre: string | null;
  puntos: PuntoEvolucion[];
  pr_historico: number | null;
}

export interface CrearSeriePayload {
  ejercicio_tipo: TipoEjercicio;
  peso: string;
  repeticiones: string;
  maquina_id?: string | null;
  nombre_libre?: string | null;
  rutina_id?: string | null;
  numero_serie?: number;
}

export interface ActualizarSeriePayload {
  peso: string;
  repeticiones: string;
}

export interface SerieConfirmada {
  id: string;
  numero_serie: number;
  peso: string;
  repeticiones: string;
}

export interface SerieEnSesion {
  id: string;
  numero_serie: number;
  peso: string;
  repeticiones: string;
}

export interface SesionDetalle {
  ejercicio: string;
  ejercicio_tipo: TipoEjercicio;
  maquina_id: string | null;
  nombre_libre: string | null;
  fecha: string;
  series: SerieEnSesion[];
}