def _login(client, email="alumno@gimnasio.com", password="alumno123"):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    return resp.get_json()["data"]["token"]


def _auth_headers(client, email="alumno@gimnasio.com", password="alumno123"):
    return {"Authorization": f"Bearer {_login(client, email, password)}"}


# ---------------- Perfil ----------------

def test_perfil_sin_token(client):
    resp = client.get("/api/usuario/perfil")
    assert resp.status_code == 401


def test_perfil_como_alumno(client):
    resp = client.get("/api/usuario/perfil", headers=_auth_headers(client))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["email"] == "alumno@gimnasio.com"
    assert data["rol"] == "alumno"
    assert "password_hash" not in data
    # Campos nuevos
    for campo in ("altura", "peso_actual", "peso_objetivo", "imagen_url",
                  "porcentaje_grasa", "fecha_medicion_grasa",
                  "origen_grasa", "cargado_por_id", "fecha_alta"):
        assert campo in data
    # IMC calculado (altura 178, peso 74.5 → 23.5)
    assert data["imc"] is not None
    assert 23.0 <= data["imc"] <= 24.0


def test_imc_null_sin_datos(client):
    """Un usuario sin altura ni peso no debe tener IMC."""
    token = _login(client, "profesor@gimnasio.com", "profe123")
    resp = client.get(
        "/api/usuario/perfil",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["imc"] is None


def test_actualizar_nombre(client):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"nombre": "Juan Pérez Actualizado"},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["nombre"] == "Juan Pérez Actualizado"


def test_actualizar_altura_y_peso(client):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"altura": 180.0, "peso_actual": 76.2},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["altura"] == 180.0
    assert data["peso_actual"] == 76.2
    # IMC recalculado: 76.2 / 1.80² = 23.5
    assert 23.0 <= data["imc"] <= 24.0


def test_actualizar_peso_objetivo(client):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"peso_objetivo": 68.0},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["peso_objetivo"] == 68.0


def test_actualizar_nombre_vacio_falla(client):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"nombre": "A"},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 400


def test_actualizar_altura_fuera_de_rango(client):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"altura": 300.0},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 400


def test_actualizar_peso_fuera_de_rango(client):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"peso_actual": 500.0},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 400


def test_no_permite_cambiar_email(client):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"email": "otro@example.com"},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 400
    assert resp.get_json()["error"]["name"] == "ForbiddenField"


def test_no_permite_cambiar_rol(client):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"rol": "profesor"},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 400


def test_no_permite_cambiar_origen_grasa(client):
    """El origen y el cargado_por_id los deriva el backend del token."""
    resp = client.patch(
        "/api/usuario/perfil",
        json={"porcentaje_grasa": 14.0, "origen_grasa": "profesor"},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 400
    assert resp.get_json()["error"]["name"] == "ForbiddenField"


def test_no_permite_cambiar_cargado_por_id(client):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"porcentaje_grasa": 14.0, "cargado_por_id": "u-pro-001"},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 400


def test_alumno_carga_grasa_deriva_origen_alumno(client):
    """El alumno carga su % grasa y el backend marca origen='alumno'."""
    token = _login(client, "alumno@gimnasio.com", "alumno123")
    resp = client.patch(
        "/api/usuario/perfil",
        json={"porcentaje_grasa": 16.5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["porcentaje_grasa"] == 16.5
    assert data["origen_grasa"] == "alumno"
    assert data["cargado_por_id"] == "u-alu-001"
    # Debe tener fecha de hoy
    assert data["fecha_medicion_grasa"] is not None


def test_profesor_carga_grasa_deriva_origen_profesor(client):
    """El profesor carga su propio % grasa y el backend marca origen='profesor'."""
    token = _login(client, "profesor@gimnasio.com", "profe123")
    resp = client.patch(
        "/api/usuario/perfil",
        json={"porcentaje_grasa": 12.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["porcentaje_grasa"] == 12.0
    assert data["origen_grasa"] == "profesor"
    assert data["cargado_por_id"] == "u-pro-001"


def test_grasa_fuera_de_rango(client):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"porcentaje_grasa": 100.0},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 400


def test_payload_vacio_falla(client):
    resp = client.patch(
        "/api/usuario/perfil",
        json={},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 400


def test_actualizar_imagen_url_valida(client):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"imagen_url": "https://example.com/foto.jpg"},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["imagen_url"] == "https://example.com/foto.jpg"


def test_actualizar_imagen_url_invalida(client):
    resp = client.patch(
        "/api/usuario/perfil",
        json={"imagen_url": "no-es-una-url"},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 400


# ---------------- Resumen ----------------

def test_resumen_sin_token(client):
    resp = client.get("/api/usuario/resumen")
    assert resp.status_code == 401


def test_resumen_como_alumno(client):
    resp = client.get("/api/usuario/resumen", headers=_auth_headers(client))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "rutinas_activas" in data
    assert "sesiones_mes" in data
    assert "racha_actual" in data
    assert data["rutinas_activas"] == 3
    assert data["sesiones_mes"] >= 1
    assert data["racha_actual"] >= 1


def test_resumen_profesor_vacio(client):
    token = _login(client, "profesor@gimnasio.com", "profe123")
    resp = client.get(
        "/api/usuario/resumen",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["rutinas_activas"] == 0
    assert data["sesiones_mes"] == 0
    assert data["racha_actual"] == 0

def test_alumno_no_recibe_notas_profesor_en_su_perfil(client):
    """
    Aunque el alumno tenga notas_profesor cargadas en el mock,
    NUNCA deben aparecer en el payload de /api/usuario/perfil.
    """
    headers = _auth_headers(client)  # login como alumno
    resp = client.get("/api/usuario/perfil", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "notas_profesor" not in data


def test_alumno_no_recibe_notas_profesor_en_me(client):
    """El endpoint /api/auth/me tampoco debe devolver notas_profesor."""
    headers = _auth_headers(client)
    resp = client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "notas_profesor" not in data


def test_alumno_no_recibe_notas_profesor_en_login(client):
    """El payload del login no debe incluir notas_profesor."""
    resp = client.post(
        "/api/auth/login",
        json={"email": "alumno@gimnasio.com", "password": "alumno123"},
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "notas_profesor" not in data["usuario"]


def test_profesor_no_recibe_notas_en_su_propio_login(client):
    """
    Un profesor tampoco tiene notas_profesor (solo los alumnos las tienen),
    pero verificamos que el campo no esté presente para evitar futuras fugas.
    """
    resp = client.post(
        "/api/auth/login",
        json={"email": "profesor@gimnasio.com", "password": "profe123"},
    )
    data = resp.get_json()["data"]["usuario"]
    assert "notas_profesor" not in data