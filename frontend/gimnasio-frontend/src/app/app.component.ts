import { Component, OnInit } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { Observable, combineLatest } from 'rxjs';
import { filter, map, startWith } from 'rxjs/operators';

import { AuthService } from './modules/auth/services/auth.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {

  mostrarBottomNav$: Observable<boolean>;
  mostrarSidebar$: Observable<boolean>;
  mostrarBannerProfesor$: Observable<boolean>;
  mostrarBannerAdmin$: Observable<boolean>;

  constructor(
    private auth: AuthService,
    private router: Router,
  ) {
    const navEnd$ = this.router.events.pipe(
      filter((e): e is NavigationEnd => e instanceof NavigationEnd),
      startWith(null),
    );

    this.mostrarBottomNav$ = combineLatest([navEnd$, this.auth.usuario$]).pipe(
      map(() => !this.router.url.startsWith('/auth')),
    );

    this.mostrarSidebar$ = combineLatest([navEnd$, this.auth.usuario$]).pipe(
      map(([_, usuario]) => {
        const url = this.router.url;
        const esAdmin = url.startsWith('/admin');
        const esGimnasio = usuario?.rol === 'gimnasio';
        const esPantallaGrande = window.innerWidth >= 1024;
        return esAdmin && esGimnasio && esPantallaGrande;
      }),
    );

    // Banner "Estás en modo admin" → cuando el admin está en /admin
    // (en mobile, porque en desktop ya tiene el sidebar con el switch)
    this.mostrarBannerAdmin$ = combineLatest([navEnd$, this.auth.usuario$]).pipe(
      map(([_, usuario]) => {
        const url = this.router.url;
        const enAdmin = url.startsWith('/admin');
        const esGimnasio = usuario?.rol === 'gimnasio';
        const sinSidebar = window.innerWidth < 1024;
        return enAdmin && esGimnasio && sinSidebar;
      }),
    );

    // Banner "Estás en modo profesor" → cuando el admin está en /profesor/*
    this.mostrarBannerProfesor$ = combineLatest([navEnd$, this.auth.usuario$]).pipe(
      map(([_, usuario]) => {
        const url = this.router.url;
        const enProfesor = url.startsWith('/profesor');
        const esGimnasio = usuario?.rol === 'gimnasio';
        return enProfesor && esGimnasio;
      }),
    );
  }

  ngOnInit(): void {
    if (this.auth.tieneToken) {
      this.auth.restaurarSesion().subscribe({ error: () => {} });
    } else {
      this.auth.marcarInicializado();
    }
  }

  irAModoProfesor(): void {
    this.router.navigate(['/profesor']);
  }

  irAModoAdmin(): void {
    this.router.navigate(['/admin']);
  }
}