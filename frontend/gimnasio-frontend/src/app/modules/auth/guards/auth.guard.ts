import { inject } from '@angular/core';
import {
  ActivatedRouteSnapshot,
  CanActivateFn,
  Router,
  RouterStateSnapshot,
} from '@angular/router';
import { map, take } from 'rxjs';

import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (
  _route: ActivatedRouteSnapshot,
  state: RouterStateSnapshot,
) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  return auth.inicializado$.pipe(
    // Esperamos a que se resuelva la restauración inicial antes de decidir.
    // Si todavía no está inicializado, esperamos a que el "me" termine.
    take(1),
    map(() => {
      if (auth.estaLogueado) return true;
      if (auth.tieneToken) {
        // Hay token pero el "me" todavía no corrió — no bloqueamos.
        // El restaurarSesion se dispara desde AppComponent (ver más abajo).
        return true;
      }
      return router.createUrlTree(['/auth'], {
        queryParams: { redirect: state.url },
      });
    }),
  );
};