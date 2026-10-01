import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { finalize } from 'rxjs/operators';

import {
  Maquina,
  GRUPOS_MUSCULARES,
  etiquetaMusculo,
} from '../../../maquinas/models/maquina.model';
import { MaquinasService } from '../../../maquinas/services/maquinas.service';

@Component({
  selector: 'app-progreso-seleccionar-ejercicio',
  templateUrl: './seleccionar-ejercicio.component.html',
  styleUrls: ['./seleccionar-ejercicio.component.scss'],
})
export class SeleccionarEjercicioComponent implements OnInit {

  maquinas: Maquina[] = [];
  filtradas: Maquina[] = [];
  cargando = false;
  errorMensaje: string | null = null;

  filtro: string | null = null;
  busqueda = '';
  nombreLibre = '';

  readonly grupos = GRUPOS_MUSCULARES;

  constructor(
    private maquinasService: MaquinasService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.cargar();
  }

  onFiltroChange(m: string | null): void {
    this.filtro = m;
    this.aplicarFiltros();
  }

  onBusquedaChange(): void {
    this.aplicarFiltros();
  }

  etiqueta(m: string): string {
    return etiquetaMusculo(m);
  }

  elegirMaquina(m: Maquina): void {
    this.router.navigate(['/progreso/registrar'], {
      queryParams: {
        tipo: 'maquina',
        maquina_id: m.id,
        nombre: m.nombre,
      },
    });
  }

  confirmarLibre(): void {
    const nombre = this.nombreLibre.trim();
    if (!nombre) return;
    this.router.navigate(['/progreso/registrar'], {
      queryParams: {
        tipo: 'libre',
        nombre,
      },
    });
  }

  reintentar(): void {
    this.cargar();
  }

  trackById(_: number, m: Maquina): string {
    return m.id;
  }

  private cargar(): void {
    this.cargando = true;
    this.errorMensaje = null;

    this.maquinasService
      .listar()
      .pipe(finalize(() => (this.cargando = false)))
      .subscribe({
        next: (data: Maquina[]) => {
          this.maquinas = data;
          this.aplicarFiltros();
        },
        error: (err: any) => {
          this.errorMensaje =
            err?.error?.error?.message ?? 'No se pudieron cargar las máquinas.';
          this.maquinas = [];
          this.filtradas = [];
        },
      });
  }

  private aplicarFiltros(): void {
    let res = this.maquinas;

    if (this.filtro) {
      res = res.filter(m =>
        m.grupos_musculares.some(
          g => g.toLowerCase() === this.filtro!.toLowerCase()
        )
      );
    }

    const q = this.busqueda.trim().toLowerCase();
    if (q) {
      res = res.filter(m => m.nombre.toLowerCase().includes(q));
    }

    this.filtradas = res;
  }
}