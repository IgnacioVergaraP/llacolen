def _login(client, email="admin@gimnasio.com", password="admin123"):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    return resp.get_json()["data"]["token"]


def _headers(client, email="admin@gimnasio.com", password="admin123"):
    return {"Authorization": f"Bearer {_login(client, email, password)}"}


_PAYLOAD = {
    "maquina_id": "mq-001",
    "tipo": "preventivo",
    "notas": "Revisión general del banco y la barra.",
}


# -------- Listar --------

def test_listar_sin_token(client):
    resp = client.get("/api/admin/mantenimientos")
    assert resp.status_code == 401


def test_listar_como_profesor_403(client):
    token = _login(client, "profesor@gimnasio.com", "profe123")
    resp = client.get(
        "/api/admin/mantenimientos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_listar_como_admin(client):
    resp = client.get("/api/admin/mantenimientos", headers=_headers(client))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 5


def test_listar_por_maquina(client):
    resp = client.get(
        "/api/admin/maquinas/mq-004/mantenimientos",
        headers=_headers(client),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["maquina"]["id"] == "mq-004"
    assert len(data["mantenimientos"]) >= 1


def test_listar_por_maquina_inexistente(client):
    resp = client.get(
        "/api/admin/maquinas/mq-999/mantenimientos",
        headers=_headers(client),
    )
    assert resp.status_code == 404


# -------- Crear --------

def test_crear_ok(client):
    resp = client.post("/api/admin/mantenimientos", json=_PAYLOAD, headers=_headers(client))
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["maquina_id"] == "mq-001"
    assert data["tipo"] == "preventivo"
    assert data["origen"] == "manual"
    assert data["realizado_por_nombre"] == "Admin Gimnasio"


def test_crear_maquina_inexistente(client):
    payload = {**_PAYLOAD, "maquina_id": "mq-999"}
    resp = client.post("/api/admin/mantenimientos", json=payload, headers=_headers(client))
    assert resp.status_code == 400


def test_crear_tipo_invalido(client):
    payload = {**_PAYLOAD, "tipo": "inventado"}
    resp = client.post("/api/admin/mantenimientos", json=payload, headers=_headers(client))
    assert resp.status_code == 400


def test_crear_sin_notas(client):
    payload = {**_PAYLOAD}
    payload.pop("notas")
    resp = client.post("/api/admin/mantenimientos", json=payload, headers=_headers(client))
    assert resp.status_code == 201
    assert resp.get_json()["data"]["notas"] is None


# -------- Eliminar --------

def test_eliminar_ok(client):
    creado = client.post("/api/admin/mantenimientos", json=_PAYLOAD, headers=_headers(client)).get_json()["data"]
    resp = client.delete(f"/api/admin/mantenimientos/{creado['id']}", headers=_headers(client))
    assert resp.status_code == 200
    assert resp.get_json()["data"]["eliminado"] is True


def test_eliminar_inexistente(client):
    resp = client.delete("/api/admin/mantenimientos/mant-999", headers=_headers(client))
    assert resp.status_code == 404


# -------- Auto-generación --------

def test_resolver_reporte_rota_genera_mantenimiento(client):
    """Crear un reporte tipo rota, resolverlo, verificar que se generó el mantenimiento."""
    token_prof = _login(client, "profesor@gimnasio.com", "profe123")
    token_admin = _login(client, "admin@gimnasio.com", "admin123")

    # Crear reporte
    reporte = client.post(
        "/api/profesor/reportes",
        json={
            "tipo": "rota",
            "prioridad": "alta",
            "descripcion": "La máquina no enciende.",
            "maquina_id": "mq-001",
        },
        headers={"Authorization": f"Bearer {token_prof}"},
    ).get_json()["data"]

    # Resolver
    client.post(
        f"/api/profesor/admin/reportes/{reporte['id']}/resolver",
        json={"resolucion": "Se reemplazó el motor."},
        headers={"Authorization": f"Bearer {token_admin}"},
    )

    # Verificar mantenimiento auto-generado
    resp = client.get(
        "/api/admin/maquinas/mq-001/mantenimientos",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    data = resp.get_json()["data"]
    autos = [m for m in data["mantenimientos"] if m["origen"] == "auto" and m["reporte_id"] == reporte["id"]]
    assert len(autos) == 1
    assert autos[0]["tipo"] == "correctivo"


def test_resolver_reporte_limpieza_no_genera(client):
    """Un reporte de limpieza no genera mantenimiento automático."""
    token_prof = _login(client, "profesor@gimnasio.com", "profe123")
    token_admin = _login(client, "admin@gimnasio.com", "admin123")

    reporte = client.post(
        "/api/profesor/reportes",
        json={
            "tipo": "limpieza",
            "prioridad": "baja",
            "descripcion": "La máquina está sucia.",
            "maquina_id": "mq-002",
        },
        headers={"Authorization": f"Bearer {token_prof}"},
    ).get_json()["data"]

    client.post(
        f"/api/profesor/admin/reportes/{reporte['id']}/resolver",
        json={"resolucion": "Se limpió."},
        headers={"Authorization": f"Bearer {token_admin}"},
    )

    resp = client.get(
        "/api/admin/maquinas/mq-002/mantenimientos",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    data = resp.get_json()["data"]
    autos = [m for m in data["mantenimientos"] if m["origen"] == "auto" and m["reporte_id"] == reporte["id"]]
    assert len(autos) == 0