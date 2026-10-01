import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, map, tap } from 'rxjs';

import { environment } from '../../../../environments/environment';
import {
  LoginRequest,
  LoginResponse,
  User,
  UserRole,
} from '../../../shared/models/user.model';
import { TokenStorageService } from '../../../shared/services/token-storage.service';

interface ApiResponse<T> {
  data: T;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {

  private readonly baseUrl = `${environment.apiUrl}/auth`;

  private readonly _usuario$ = new BehaviorSubject<User | null>(null);
  readonly usuario$ = this._usuario$.asObservable();

  private readonly _inicializado$ = new BehaviorSubject<boolean>(false);
  readonly inicializado$ = this._inicializado$.asObservable();

  constructor(
    private http: HttpClient,
    private tokenStorage: TokenStorageService,
    private router: Router,
  ) {}

  get usuarioActual(): User | null {
    return this._usuario$.value;
  }

  get estaLogueado(): boolean {
    return this._usuario$.value !== null;
  }

  get tieneToken(): boolean {
    return !!this.tokenStorage.getToken();
  }

  tieneRol(...roles: UserRole[]): boolean {
    const u = this._usuario$.value;
    return !!u && roles.includes(u.rol);
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http
      .post<ApiResponse<LoginResponse>>(`${this.baseUrl}/login`, credentials)
      .pipe(
        map(res => res.data),
        tap(data => {
          this.tokenStorage.setToken(data.token);
          this._usuario$.next(data.usuario);
          this._inicializado$.next(true);
        }),
      );
  }

  restaurarSesion(): Observable<User> {
    return this.http.get<ApiResponse<User>>(`${this.baseUrl}/me`).pipe(
      map(res => res.data),
      tap({
        next: user => {
          this._usuario$.next(user);
          this._inicializado$.next(true);
        },
        error: () => {
          // Si falla, limpiamos y marcamos inicializado.
          this.tokenStorage.clear();
          this._usuario$.next(null);
          this._inicializado$.next(true);
        },
      }),
    );
  }

  marcarInicializado(): void {
    this._inicializado$.next(true);
  }

  logout(redirect = true): void {
    this.tokenStorage.clear();
    this._usuario$.next(null);
    if (redirect) {
      this.router.navigate(['/auth']);
    }
  }
}