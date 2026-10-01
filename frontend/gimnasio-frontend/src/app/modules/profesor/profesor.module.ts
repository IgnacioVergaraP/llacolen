import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { ProfesorRoutingModule } from './profesor-routing.module';
import { SharedModule } from '../../shared/shared.module';

import { InicioComponent } from './pages/inicio/inicio.component';
import { ListaAlumnosComponent } from './pages/lista-alumnos/lista-alumnos.component';
import { DetalleAlumnoComponent } from './pages/detalle-alumno/detalle-alumno.component';
import { SubirEjercicioComponent } from './pages/subir-ejercicio/subir-ejercicio.component';
import { ReportarComponent } from './pages/reportar/reportar.component';
import { PerfilProfesorComponent } from './pages/perfil-profesor/perfil-profesor.component';
import { SolicitudesRutinaComponent } from './pages/solicitudes-rutina/solicitudes-rutina.component';
import { RutinasListaComponent } from './pages/rutinas-lista/rutinas-lista.component';
import { RutinaBuilderComponent } from './pages/rutina-builder/rutina-builder.component';
import { MisHorariosComponent } from './pages/mis-horarios/mis-horarios.component';

import { AlumnoCardComponent } from './components/alumno-card/alumno-card.component';
import { MaquinaPickerComponent } from './components/maquina-picker/maquina-picker.component';
import { EjercicioBuilderCardComponent } from './components/ejercicio-builder-card/ejercicio-builder-card.component';
import { RutinaCardProfesorComponent } from './components/rutina-card-profesor/rutina-card-profesor.component';
import { TabPerfilComponent } from './components/detalle-alumno-tabs/tab-perfil/tab-perfil.component';
import { TabRutinasComponent } from './components/detalle-alumno-tabs/tab-rutinas/tab-rutinas.component';
import { TabProgresoComponent } from './components/detalle-alumno-tabs/tab-progreso/tab-progreso.component';
import { TabSolicitudesComponent } from './components/detalle-alumno-tabs/tab-solicitudes/tab-solicitudes.component';

@NgModule({
  declarations: [
    InicioComponent,
    ListaAlumnosComponent,
    DetalleAlumnoComponent,
    SubirEjercicioComponent,
    ReportarComponent,
    PerfilProfesorComponent,
    SolicitudesRutinaComponent,
    RutinasListaComponent,
    RutinaBuilderComponent,
    MisHorariosComponent,
    AlumnoCardComponent,
    MaquinaPickerComponent,
    EjercicioBuilderCardComponent,
    RutinaCardProfesorComponent,
    TabPerfilComponent,
    TabRutinasComponent,
    TabProgresoComponent,
    TabSolicitudesComponent,
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    SharedModule,
    ProfesorRoutingModule,
  ],
})
export class ProfesorModule {}