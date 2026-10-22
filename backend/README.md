# Backend de Llacolén

API Flask con Supabase como servicio de base de datos y autenticación.

## Desarrollo local

Desde `backend/`:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python wsgi.py
```

Completa las variables de `.env` antes de usar las rutas que acceden a Supabase.
La comprobación de disponibilidad está en `http://localhost:5000/api/health`.

## Desplegar en Vercel

Crea un **proyecto nuevo para el backend**, importando este mismo repositorio.
El proyecto del frontend conserva su propia configuración.

1. Configura **Root Directory** como `backend`.
2. Usa el preset **Flask**, sin sobrescribir Build Command ni Output Directory.
   `vercel.json` selecciona Flask y `server.py` exporta la aplicación existente.
   `.python-version` fija Python 3.12; las dependencias se instalan desde
   `requirements.txt`. No hace falta ejecutar Gunicorn como comando de inicio.
3. En **Settings → Environment Variables**, carga las siguientes variables para
   Production y, si vas a probar despliegues de preview, también para Preview:

   | Variable | Valor |
   | --- | --- |
   | `FLASK_ENV` | `production` |
   | `SECRET_KEY` | Un secreto aleatorio para producción |
   | `SUPABASE_URL` | La URL del proyecto Supabase actual |
   | `SUPABASE_SERVICE_ROLE_KEY` | La clave privada actual, solo en el backend |
   | `SUPABASE_ANON_KEY` | La clave pública del proyecto actual |
   | `SUPABASE_JWT_SECRET` | El secreto JWT actual, si usas tokens HS256 |
   | `CORS_ORIGINS` | `https://llacolen.vercel.app,capacitor://localhost,http://localhost:4200,http://127.0.0.1:4200` |

   Ajusta `CORS_ORIGINS` si el frontend usa otro dominio. Los orígenes van sin
   `/api` ni barra final. `.env` no se sube; configura las variables en Vercel.
4. Despliega y comprueba `https://<dominio-backend>/api/health`. Debe responder
   con `data.status` igual a `ok`. Comprueba también el login y una ruta con
   autenticación desde el frontend para verificar Supabase y CORS.
5. Cambia `apiUrl` en ambos archivos del frontend:
   - `frontend/gimnasio-frontend/src/environments/environment.ts`
   - `frontend/gimnasio-frontend/src/environments/environment.prod.ts`

   Usa `https://<dominio-backend>/api` y vuelve a desplegar el frontend.
   Si distribuyes la aplicación con Capacitor, recompila y sincroniza también
   las aplicaciones móviles para que reciban la nueva URL.
6. Mantén Railway activo hasta comprobar los flujos de la web y de las
   aplicaciones móviles que sigan usando su URL.

La base de datos y los usuarios permanecen en el proyecto Supabase actual.
Las migraciones SQL de `scripts/migrations/` se ejecutan en Supabase cuando
corresponda; el despliegue de Vercel no las ejecuta automáticamente.

Documentación: [Flask en Vercel](https://vercel.com/docs/frameworks/backend/flask).
