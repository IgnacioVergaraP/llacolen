export type RangoAnalytics = '7d' | '30d' | '90d' | '365d';

export interface MaquinaUso {
  maquina_id: string;
  maquina_nombre: string;
  cantidad_series: number;
}

export interface DashboardUso {
  rango: RangoAnalytics;
  dias: number;
  total_series: number;
  total_maquinas_usadas: number;
  top_usadas: MaquinaUso[];
  menos_usadas: MaquinaUso[];
}

export type TipoMantenimiento = 'preventivo' | 'correctivo' | 'limpieza' | 'revision';

export type OrigenMantenimiento = 'manual' | 'auto';

export interface Mantenimiento {
  id: string;
  maquina_id: string;
  maquina_nombre: string;
  fecha: string;
  tipo: TipoMantenimiento;
  notas: string | null;
  realizado_por_id: string | null;
  realizado_por_nombre: string | null;
  origen: OrigenMantenimiento;
  reporte_id: string | null;
}

export interface MaquinaMantenimientosResponse {
  maquina: {
    id: string;
    nombre: string;
    grupos_musculares: string[];
    descripcion: string;
    video_url: string;
    imagen_url: string;
  };
  mantenimientos: Mantenimiento[];
}

export interface CrearMantenimientoPayload {
  maquina_id: string;
  tipo: TipoMantenimiento;
  notas?: string | null;
  fecha?: string | null;      // 'YYYY-MM-DD' o null (default: hoy)
}

export const TIPOS_MANTENIMIENTO: { value: TipoMantenimiento; label: string }[] = [
  { value: 'preventivo', label: 'Preventivo' },
  { value: 'correctivo', label: 'Correctivo' },
  { value: 'limpieza',   label: 'Limpieza' },
  { value: 'revision',   label: 'Revisión' },
];

export function etiquetaTipoMantenimiento(t: TipoMantenimiento): string {
  return TIPOS_MANTENIMIENTO.find(x => x.value === t)?.label ?? t;
}

export const RANGOS: { value: RangoAnalytics; label: string }[] = [
  { value: '7d',   label: 'Últimos 7 días' },
  { value: '30d',  label: 'Últimos 30 días' },
  { value: '90d',  label: 'Últimos 90 días' },
  { value: '365d', label: 'Último año' },
];