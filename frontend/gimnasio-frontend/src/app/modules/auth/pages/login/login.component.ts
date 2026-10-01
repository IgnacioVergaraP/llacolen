import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent {

  form: FormGroup;
  enviando = false;
  errorMensaje: string | null = null;

  constructor(
    private fb: FormBuilder,
    private auth: AuthService,
    private router: Router,
    private route: ActivatedRoute,
  ) {
    this.form = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(4)]],
    });
  }

  get emailCtrl() { return this.form.get('email')!; }
  get passwordCtrl() { return this.form.get('password')!; }

  onSubmit(): void {
  this.errorMensaje = null;

  if (this.form.invalid) {
    this.form.markAllAsTouched();
    return;
  }

  this.enviando = true;

  this.auth.login(this.form.value).subscribe({
    next: () => {
      this.enviando = false;
      const redirect = this.route.snapshot.queryParamMap.get('redirect');
      const defaultRoute = this.auth.usuarioActual?.rol === 'gimnasio' ? '/admin' : '/maquinas';
      this.router.navigateByUrl(redirect || defaultRoute);
    },
    error: err => {
      this.enviando = false;
      this.errorMensaje = err?.error?.error?.message ?? 'No se pudo iniciar sesión.';
    },
  });
}
}