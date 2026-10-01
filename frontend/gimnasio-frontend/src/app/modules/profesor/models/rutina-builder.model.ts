import { Ejercicio } from '../../rutinas/models/rutina.model';

/** Ejercicio en el builder: puede ser nuevo o existente. */
export interface EjercicioBuilder {
  uid: string;
  tipo: 'maquina' | 'libre';
  series: number;
  repeticiones: string;
  peso_sugerido: string;
  maquina_id: string | null;
  maquina_nombre?: string | null;
  nombre?: string | null;
  descripcion?: string | null;
  /** Si está minimizado, la card se ve compacta. */
  minimizado: boolean;
}

export interface CrearRutinaPayload {
  alumno_id: string;
  titulo: string;
  grupos_musculares: string[];
  ejercicios: {
    id?: string;
    tipo: 'maquina' | 'libre';
    series: number;
    repeticiones: string;
    peso_sugerido: string;
    maquina_id?: string | null;
    nombre?: string | null;
    descripcion?: string | null;
  }[];
}

export interface EditarRutinaPayload {
  titulo: string;
  grupos_musculares: string[];
  ejercicios: {
    id?: string;
    tipo: 'maquina' | 'libre';
    series: number;
    repeticiones: string;
    peso_sugerido: string;
    maquina_id?: string | null;
    nombre?: string | null;
    descripcion?: string | null;
  }[];
}

export interface DuplicarRutinaPayload {
  nuevo_alumno_id: string;
}

export interface EditarDatosAlumnoPayload {
  peso_actual?: number | null;
  peso_objetivo?: number | null;
  porcentaje_grasa?: number | null;
  notas_profesor?: string | null;
}

export function generarUid(): string {
  return 'b-' + Math.random().toString(36).slice(2, 10);
}

export function ejercicioExistenteABuilder(e: Ejercicio): EjercicioBuilder {
  return {
    uid: e.id,
    tipo: e.tipo,
    series: e.series,
    repeticiones: e.repeticiones,
    peso_sugerido: e.peso_sugerido ?? '',
    maquina_id: e.maquina_id ?? null,
    maquina_nombre: e.maquina?.nombre ?? null,
    nombre: e.nombre ?? null,
    descripcion: e.descripcion ?? null,
    minimizado: false,
  };
}