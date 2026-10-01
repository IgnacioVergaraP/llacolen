import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { environment } from '../../../../environments/environment';
import { Rutina } from '../models/rutina.model';

interface ApiResponse<T> {
  data: T;
}

@Injectable({
  providedIn: 'root',
})
export class RutinasService {

  private readonly baseUrl = `${environment.apiUrl}/rutinas`;

  constructor(private http: HttpClient) {}

  listar(incluirInactivas = false): Observable<Rutina[]> {
    const q = incluirInactivas ? '?incluir_inactivas=true' : '';
    return this.http
      .get<ApiResponse<Rutina[]>>(`${this.baseUrl}${q}`)
      .pipe(map(res => res.data));
  }

  obtenerDetalle(id: string): Observable<Rutina> {
    return this.http
      .get<ApiResponse<Rutina>>(`${this.baseUrl}/${id}`)
      .pipe(map(res => res.data));
  }
}