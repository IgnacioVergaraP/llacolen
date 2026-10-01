import { inject } from '@angular/core';
import {
  HttpErrorResponse,
  HttpEvent,
  HttpHandlerFn,
  HttpInterceptorFn,
  HttpRequest,
} from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

import { AuthService } from '../services/auth.service';
import { TokenStorageService } from '../../../shared/services/token-storage.service';

export const authInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn,
) => {
  const tokenStorage = inject(TokenStorageService);
  const auth = inject(AuthService);

  const token = tokenStorage.getToken();

  // Clonamos la request agregando headers:
  //   1. Authorization: Bearer <token> (excepto en /auth/login)
  //   2. ngrok-skip-browser-warning: evita la interstitial de ngrok free
  const esLogin = req.url.includes('/auth/login');

  const headers: Record<string, string> = {
    'ngrok-skip-browser-warning': 'true',
  };

  if (token && !esLogin) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const autenticada = req.clone({ setHeaders: headers });

  return next(autenticada).pipe(
    catchError((err: HttpErrorResponse) => {
      if (err.status === 401 && !esLogin) {
        auth.logout(true);
      }
      return throwError(() => err);
    }),
  );
};