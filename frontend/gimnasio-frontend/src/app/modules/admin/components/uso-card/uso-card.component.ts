import { Component, Input } from '@angular/core';
import { MaquinaUso } from '../../models/analytics.model';

@Component({
  selector: 'app-uso-card',
  templateUrl: './uso-card.component.html',
  styleUrls: ['./uso-card.component.scss'],
})
export class UsoCardComponent {

  @Input() maquina!: MaquinaUso;
  @Input() maximo = 1;
  @Input() variante: 'top' | 'baja' = 'top';

  get porcentaje(): number {
    if (this.maximo <= 0) return 0;
    const pct = (this.maquina.cantidad_series / this.maximo) * 100;
    return Math.max(4, Math.min(100, Math.round(pct)));
  }
}