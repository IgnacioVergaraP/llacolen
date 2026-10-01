import { Injectable } from '@angular/core';

const TOKEN_KEY = 'gimnasio.auth.token';

@Injectable({
  providedIn: 'root',
})
export class TokenStorageService {

  getToken(): string | null {
    try {
      return localStorage.getItem(TOKEN_KEY);
    } catch {
      return null;
    }
  }

  setToken(token: string): void {
    try {
      localStorage.setItem(TOKEN_KEY, token);
    } catch {
      // Silencioso: si no hay storage (SSR, modo privado), igual no rompemos.
    }
  }

  clear(): void {
    try {
      localStorage.removeItem(TOKEN_KEY);
    } catch {
      // ignorar
    }
  }
}