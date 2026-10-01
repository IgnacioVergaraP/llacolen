import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { finalize } from 'rxjs/operators';

import { Ejercicio, Rutina } from '../../models/rutina.model';
import { RutinasService } from '../../services/rutinas.service';

@Component({
  selector: 'app-rutinas-detalle',
  templateUrl: './detalle.component.html',
  styleUrls: ['./detalle.component.scss'],
})
export class DetalleComponent implements OnInit {

  rutina: Rutina | null = null;
  cargando = false;
  errorMensaje: string | null = null;

  sheetVisible = false;
  ejercicioEnSheet: Ejercicio | null = null;

  sheetVideoUrlSeguro: SafeResourceUrl | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private rutinasService: RutinasService,
    private sanitizer: DomSanitizer,
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.errorMensaje = 'Rutina no encontrada.';
      return;
    }
    this.cargar(id);
  }

  reintentar(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) this.cargar(id);
  }

  abrirSheet(ejercicio: Ejercicio): void {
    this.ejercicioEnSheet = ejercicio;
    this.sheetVideoUrlSeguro = this.construirVideoUrlSeguro(ejercicio);
    this.sheetVisible = true;
  }

  cerrarSheet(): void {
    this.sheetVisible = false;
    setTimeout(() => {
      this.ejercicioEnSheet = null;
      this.sheetVideoUrlSeguro = null;
    }, 250);
  }

  get sheetEsMaquina(): boolean {
    return this.ejercicioEnSheet?.tipo === 'maquina';
  }

  get sheetEsLibre(): boolean {
    return this.ejercicioEnSheet?.tipo === 'libre';
  }

  get sheetTitulo(): string {
    if (!this.ejercicioEnSheet) return '';
    return this.sheetEsMaquina
      ? (this.ejercicioEnSheet.maquina?.nombre ?? 'Máquina')
      : (this.ejercicioEnSheet.nombre ?? 'Ejercicio');
  }

  get sheetDescripcion(): string | null {
    if (!this.ejercicioEnSheet) return null;
    return this.sheetEsMaquina
      ? (this.ejercicioEnSheet.maquina?.descripcion ?? null)
      : (this.ejercicioEnSheet.descripcion ?? null);
  }

  get sheetResumenSeries(): string {
    if (!this.ejercicioEnSheet) return '';
    return `${this.ejercicioEnSheet.series} × ${this.ejercicioEnSheet.repeticiones}`;
  }

  verDetalleMaquina(): void {
    if (!this.ejercicioEnSheet?.maquina_id) return;
    const id = this.ejercicioEnSheet.maquina_id;
    this.cerrarSheet();
    this.router.navigate(['/maquinas', id]);
  }

  registrarSeries(): void {
    if (!this.ejercicioEnSheet || !this.rutina) return;

    const ej = this.ejercicioEnSheet;
    const esMaquina = ej.tipo === 'maquina';

    this.cerrarSheet();

    this.router.navigate(['/progreso/registrar'], {
      queryParams: {
        tipo: ej.tipo,
        maquina_id: esMaquina ? (ej.maquina_id ?? null) : null,
        nombre: esMaquina
          ? (ej.maquina?.nombre ?? ej.maquina_id ?? '')
          : (ej.nombre ?? ''),
        rutina_id: this.rutina.id,
        series: ej.series,
        peso: ej.peso_sugerido ?? null,
        repeticiones: ej.repeticiones,
      },
    });
  }

  trackByEjercicio(_: number, e: Ejercicio): string {
    return e.id;
  }

  private construirVideoUrlSeguro(ejercicio: Ejercicio): SafeResourceUrl | null {
    if (ejercicio.tipo !== 'maquina') return null;
    const url = ejercicio.maquina?.video_url;
    if (!url) return null;
    return this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }

  private cargar(id: string): void {
    this.cargando = true;
    this.errorMensaje = null;

    this.rutinasService
      .obtenerDetalle(id)
      .pipe(finalize(() => (this.cargando = false)))
      .subscribe({
        next: (r: Rutina) => (this.rutina = r),
        error: (err: any) => {
          this.errorMensaje =
            err?.error?.error?.message ?? 'No se pudo cargar la rutina.';
          this.rutina = null;
        },
      });
  }
}