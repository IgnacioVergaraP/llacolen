"""
Crea los usuarios de prueba en Supabase Auth y setea sus roles en app_metadata.

Uso (desde backend/):
    python -m scripts.seed_supabase_users

Requiere que SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY estén seteados en .env.
Es idempotente: si un usuario ya existe, actualiza app_metadata y perfil.
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not URL or not KEY:
    print("ERROR: faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en .env")
    sys.exit(1)

sb = create_client(URL, KEY)


USUARIOS = [
    # --- gimnasio (admin) ---
    {
        "email": "admin@gimnasio.com",
        "password": "admin123",
        "nombre": "Admin Gimnasio",
        "rol": "gimnasio",
        "perfil": {
            "fecha_alta": "2024-01-15T00:00:00+00:00",
        },
    },
    # --- profesor ---
    {
        "email": "profesor@gimnasio.com",
        "password": "profe123",
        "nombre": "Prof. Martínez",
        "rol": "profesor",
        "perfil": {
            "bio": "Especialista en hipertrofia y fuerza. 8 años acompañando alumnos en su progreso.",
            "especialidades": ["musculación", "fuerza", "hipertrofia"],
            "anios_experiencia": 8,
            "telefono": "+54 11 5555-1234",
            "fecha_alta": "2024-03-08T00:00:00+00:00",
        },
    },
    # --- alumnos ---
    {
        "email": "alumno@gimnasio.com",
        "password": "alumno123",
        "nombre": "Juan Pérez",
        "rol": "alumno",
        "perfil": {
            "altura": 178.0,
            "peso_actual": 74.5,
            "peso_objetivo": 70.0,
            "porcentaje_grasa": 14.5,
            "fecha_medicion_grasa": "2026-09-15",
            "origen_grasa": "profesor",
            "notas_profesor": "Buena técnica en press de banca. Trabajar movilidad de hombro derecho.",
            "fecha_alta": "2025-06-20T00:00:00+00:00",
        },
    },
    {
        "email": "maria.gonzalez@gimnasio.com",
        "password": "maria123",
        "nombre": "María González",
        "rol": "alumno",
        "perfil": {
            "altura": 165.0,
            "peso_actual": 58.0,
            "peso_objetivo": 60.0,
            "porcentaje_grasa": 22.0,
            "fecha_medicion_grasa": "2026-09-10",
            "origen_grasa": "profesor",
            "fecha_alta": "2025-09-12T00:00:00+00:00",
        },
    },
    {
        "email": "carlos.rodriguez@gimnasio.com",
        "password": "carlos123",
        "nombre": "Carlos Rodríguez",
        "rol": "alumno",
        "perfil": {
            "altura": 182.0,
            "peso_actual": 88.0,
            "peso_objetivo": 80.0,
            "porcentaje_grasa": 18.5,
            "fecha_medicion_grasa": "2026-09-20",
            "origen_grasa": "profesor",
            "fecha_alta": "2025-11-03T00:00:00+00:00",
        },
    },
    {
        "email": "lucia.fernandez@gimnasio.com",
        "password": "lucia123",
        "nombre": "Lucía Fernández",
        "rol": "alumno",
        "perfil": {
            "altura": 170.0,
            "peso_actual": 62.0,
            "fecha_alta": "2026-01-08T00:00:00+00:00",
        },
    },
]


def _find_user_by_email(email: str):
    """Busca un usuario en auth.users por email usando la Admin API."""
    try:
        # list_users no filtra por email, pero con 6 usuarios alcanza
        resp = sb.auth.admin.list_users()
        for u in resp:
            if u.email == email:
                return u
    except Exception as e:
        print(f"Error listando usuarios: {e}")
    return None


def main():
    for u in USUARIOS:
        print(f"Procesando {u['email']}...")
        existing = _find_user_by_email(u["email"])

        if existing:
            print(f"  Ya existe. Actualizando app_metadata y perfil...")
            user_id = existing.id
            # Actualizar app_metadata con el rol
            try:
                sb.auth.admin.update_user_by_id(
                    user_id,
                    {"app_metadata": {"rol": u["rol"]}},
                )
            except Exception as e:
                print(f"  ERROR actualizando app_metadata: {e}")
                continue
        else:
            # Crear usuario
            try:
                resp = sb.auth.admin.create_user({
                    "email": u["email"],
                    "password": u["password"],
                    "email_confirm": True,
                    "user_metadata": {
                        "nombre": u["nombre"],
                        "rol": u["rol"],
                    },
                    "app_metadata": {
                        "rol": u["rol"],
                    },
                })
                user_id = resp.user.id
                print(f"  Creado: {user_id}")
            except Exception as e:
                print(f"  ERROR creando: {e}")
                continue

        # Actualizar el perfil en public.profiles con los datos extra
        perfil_update = {
            "nombre": u["nombre"],
            "rol": u["rol"],
            **u.get("perfil", {}),
        }
        try:
            sb.table("profiles").update(perfil_update).eq("id", user_id).execute()
            print(f"  Perfil actualizado.")
        except Exception as e:
            print(f"  ERROR actualizando perfil: {e}")

    print("\nListo.")


if __name__ == "__main__":
    main()