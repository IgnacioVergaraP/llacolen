import { Component, OnInit } from '@angular/core';
import { finalize } from 'rxjs/operators';

import { AdminService } from '../../services/admin.service';
import {
  DashboardUso,
  RANGOS,
  RangoAnalytics,
} from '../../models/analytics.model';

type VistaRanking = 'top' | 'bottom';

@Component({
  selector: 'app-admin-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit {

  rango: RangoAnalytics = '30d';
  vista: VistaRanking = 'top';
  data: DashboardUso | null = null;

  cargando = false;
  errorMensaje: string | null = null;

  readonly rangos = RANGOS;

  constructor(private adminService: AdminService) {}

  ngOnInit(): void {
    this.cargar();
  }

  setRango(r: RangoAnalytics): void {
    if (this.rango === r) return;
    this.rango = r;
    this.cargar();
  }

  setVista(v: VistaRanking): void {
    this.vista = v;
  }

  reintentar(): void { this.cargar(); }

  get lista(): { maquina_id: string; maquina_nombre: string; cantidad_series: number }[] {
    if (!this.data) return [];
    return this.vista === 'top' ? this.data.top_usadas : this.data.menos_usadas;
  }

  get maximo(): number {
    if (this.lista.length === 0) return 1;
    const max = Math.max(...this.lista.map(m => m.cantidad_series));
    return max > 0 ? max : 1;
  }

  get tituloVista(): string {
    return this.vista === 'top' ? 'Más usadas' : 'Menos usadas';
  }

  get iconoVista(): string {
    return this.vista === 'top' ? 'bi-trophy' : 'bi-exclamation-circle';
  }

  private cargar(): void {
    this.cargando = true;
    this.errorMensaje = null;

    this.adminService
      .obtenerDashboardUso(this.rango)
      .pipe(finalize(() => (this.cargando = false)))
      .subscribe({
        next: (d) => (this.data = d),
        error: (err: any) => {
          this.errorMensaje = err?.error?.error?.message ?? 'No se pudo cargar el dashboard.';
          this.data = null;
        },
      });
  }
}