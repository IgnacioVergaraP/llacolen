"""
Tests del blueprint usuario.

Todos usan mock_auth para autenticarse (sin llamadas a Supabase).
"""


# -------- Perfil --------

def test_perfil_sin_token(client):
    resp = client.get("/api/usuario/perfil")
    assert resp.status_code == 401


def test_perfil_como_alumno(client, mock_auth):
    resp = client.get("/api/usuario/perfil", headers=mock_auth.as_alumno())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["email"] == "alumno@gimnasio.com"
    assert data["rol"] == "alumno"
    assert "password_hash" not in data
    # Campos presentes
    for campo in ("altura", "peso_actual", "peso_objetivo", "imagen_url",
                  "porcentaje_grasa", "fecha_medicion_grasa",
                  "origen_grasa", "cargado_por_id", "fecha_alta"):
        assert campo in data
    # IMC calculado
    assert data["imc"] is not None
    assert 23.0 <= data["imc"] <= 24.0


def test_imc_null_sin_datos(client, mock_auth):
    """El profesor no tiene altura/peso cargados → IMC null."""
    resp = client.get("/api/usuario/perfil", headers=mock_auth.as_profesor())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["imc"] is None


def test_alumno_no_recibe_notas_profesor_en_su_perfil(client, mock_auth):
    """El campo notas_profesor nunca aparece para el propio alumno."""
    resp = client.get("/api/usuario/perfil", headers=mock_auth.as_alumno())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "notas_profesor" not in data


def test_alumno_no_recibe_notas_profesor_en_me(client, mock_auth):
    resp = client.get("/api/auth/me", headers=mock_auth.as_alumno())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "notas_profesor" not in data


def test_profesor_si_recibe_notas_profesor_del_alumno(client, mock_auth):
    """El profesor consultando el perfil de un alumno sí ve notas_profesor."""
    resp = client.get(
        "/api/profesor/alumnos/u-alu-001/perfil",
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "notas_profesor" in data["perfil"]


def test_admin_si_recibe_notas_profesor_del_alumno(client, mock_auth):
    resp = client.get(
        "/api/profesor/alumnos/u-alu-001/perfil",
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "notas_profesor" in data["perfil"]


# -------- Actualizar perfil --------

def test_actualizar_nombre(client, mock_auth):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"nombre": "Juan Pérez Actualizado"},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["nombre"] == "Juan Pérez Actualizado"


def test_actualizar_altura_y_peso(client, mock_auth):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"altura": 180.0, "peso_actual": 76.2},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["altura"] == 180.0
    assert data["peso_actual"] == 76.2
    assert 23.0 <= data["imc"] <= 24.0


def test_actualizar_peso_objetivo(client, mock_auth):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"peso_objetivo": 68.0},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["peso_objetivo"] == 68.0


def test_actualizar_nombre_vacio_falla(client, mock_auth):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"nombre": "A"},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400


def test_actualizar_altura_fuera_de_rango(client, mock_auth):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"altura": 300.0},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400


def test_actualizar_peso_fuera_de_rango(client, mock_auth):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"peso_actual": 500.0},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400


def test_no_permite_cambiar_email(client, mock_auth):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"email": "otro@example.com"},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400
    assert resp.get_json()["error"]["name"] == "ForbiddenField"


def test_no_permite_cambiar_rol(client, mock_auth):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"rol": "profesor"},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400


def test_no_permite_cambiar_origen_grasa(client, mock_auth):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"porcentaje_grasa": 14.0, "origen_grasa": "profesor"},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400
    assert resp.get_json()["error"]["name"] == "ForbiddenField"


def test_no_permite_cambiar_cargado_por_id(client, mock_auth):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"porcentaje_grasa": 14.0, "cargado_por_id": "u-pro-001"},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400


def test_alumno_carga_grasa_deriva_origen_alumno(client, mock_auth):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"porcentaje_grasa": 16.5},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["porcentaje_grasa"] == 16.5
    assert data["origen_grasa"] == "alumno"
    assert data["cargado_por_id"] == "u-alu-001"
    assert data["fecha_medicion_grasa"] is not None


def test_profesor_carga_grasa_deriva_origen_profesor(client, mock_auth):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"porcentaje_grasa": 12.0},
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["porcentaje_grasa"] == 12.0
    assert data["origen_grasa"] == "profesor"
    assert data["cargado_por_id"] == "u-pro-001"


def test_grasa_fuera_de_rango(client, mock_auth):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"porcentaje_grasa": 100.0},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400


def test_payload_vacio_falla(client, mock_auth):
    resp = client.patch(
        "/api/usuario/perfil",
        json={},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400


def test_actualizar_imagen_url_valida(client, mock_auth):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"imagen_url": "https://example.com/foto.jpg"},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["imagen_url"] == "https://example.com/foto.jpg"


def test_actualizar_imagen_url_invalida(client, mock_auth):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"imagen_url": "no-es-una-url"},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400


# -------- Resumen --------

def test_resumen_sin_token(client):
    resp = client.get("/api/usuario/resumen")
    assert resp.status_code == 401


def test_resumen_como_alumno(client, mock_auth):
    resp = client.get("/api/usuario/resumen", headers=mock_auth.as_alumno())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "rutinas_activas" in data
    assert "sesiones_mes" in data
    assert "racha_actual" in data
    assert data["rutinas_activas"] == 3
    assert data["sesiones_mes"] >= 1
    assert data["racha_actual"] >= 1


def test_resumen_profesor_vacio(client, mock_auth):
    resp = client.get("/api/usuario/resumen", headers=mock_auth.as_profesor())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["rutinas_activas"] == 0
    assert data["sesiones_mes"] == 0
    assert data["racha_actual"] == 0