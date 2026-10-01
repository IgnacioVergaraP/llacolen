import { Component, OnInit } from '@angular/core';
import { finalize } from 'rxjs/operators';

import { Maquina } from '../../models/maquina.model';
import { MaquinasService } from '../../services/maquinas.service';

@Component({
  selector: 'app-maquinas-lista',
  templateUrl: './lista.component.html',
  styleUrls: ['./lista.component.scss'],
})
export class ListaComponent implements OnInit {

  maquinas: Maquina[] = [];
  cargando = false;
  errorMensaje: string | null = null;
  musculoSeleccionado: string | null = null;

  constructor(private maquinasService: MaquinasService) {}

  ngOnInit(): void {
    this.cargar();
  }

  onMusculoChange(musculo: string | null): void {
    this.musculoSeleccionado = musculo;
    this.cargar();
  }

  reintentar(): void {
    this.cargar();
  }

  private cargar(): void {
    this.cargando = true;
    this.errorMensaje = null;

    const peticion$ = this.musculoSeleccionado
      ? this.maquinasService.listarPorMusculo(this.musculoSeleccionado)
      : this.maquinasService.listar();

    peticion$
      .pipe(finalize(() => (this.cargando = false)))
      .subscribe({
        next: (data: Maquina[]) => (this.maquinas = data),
        error: (err: any) => {
          this.errorMensaje =
            err?.error?.error?.message ?? 'No se pudieron cargar las máquinas.';
          this.maquinas = [];
        },
      });
  }

  trackById(_: number, m: Maquina): string {
    return m.id;
  }
}