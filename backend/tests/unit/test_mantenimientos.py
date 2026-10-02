"""
Tests de mantenciones (blueprint admin).
"""


_PAYLOAD = {
    "maquina_id": "mq-001",
    "tipo": "preventivo",
    "notas": "Revisión general del banco y la barra.",
}


# -------- Listar --------

def test_listar_sin_token(client):
    resp = client.get("/api/admin/mantenimientos")
    assert resp.status_code == 401


def test_listar_como_profesor_403(client, mock_auth):
    resp = client.get("/api/admin/mantenimientos", headers=mock_auth.as_profesor())
    assert resp.status_code == 403


def test_listar_como_admin(client, mock_auth):
    resp = client.get("/api/admin/mantenimientos", headers=mock_auth.as_admin())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 5


def test_listar_por_maquina(client, mock_auth):
    resp = client.get(
        "/api/admin/maquinas/mq-004/mantenimientos",
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["maquina"]["id"] == "mq-004"
    assert len(data["mantenimientos"]) >= 1


def test_listar_por_maquina_inexistente(client, mock_auth):
    resp = client.get(
        "/api/admin/maquinas/mq-999/mantenimientos",
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 404


# -------- Crear --------

def test_crear_ok(client, mock_auth):
    resp = client.post("/api/admin/mantenimientos", json=_PAYLOAD, headers=mock_auth.as_admin())
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["maquina_id"] == "mq-001"
    assert data["tipo"] == "preventivo"
    assert data["origen"] == "manual"
    assert data["realizado_por_nombre"] == "Admin Gimnasio"


def test_crear_maquina_inexistente(client, mock_auth):
    payload = {**_PAYLOAD, "maquina_id": "mq-999"}
    resp = client.post("/api/admin/mantenimientos", json=payload, headers=mock_auth.as_admin())
    assert resp.status_code == 400


def test_crear_tipo_invalido(client, mock_auth):
    payload = {**_PAYLOAD, "tipo": "inventado"}
    resp = client.post("/api/admin/mantenimientos", json=payload, headers=mock_auth.as_admin())
    assert resp.status_code == 400


def test_crear_sin_notas(client, mock_auth):
    payload = {**_PAYLOAD}
    payload.pop("notas")
    resp = client.post("/api/admin/mantenimientos", json=payload, headers=mock_auth.as_admin())
    assert resp.status_code == 201
    assert resp.get_json()["data"]["notas"] is None


# -------- Eliminar --------

def test_eliminar_ok(client, mock_auth):
    creado = client.post(
        "/api/admin/mantenimientos", json=_PAYLOAD, headers=mock_auth.as_admin()
    ).get_json()["data"]
    resp = client.delete(
        f"/api/admin/mantenimientos/{creado['id']}",
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["eliminado"] is True


def test_eliminar_inexistente(client, mock_auth):
    resp = client.delete("/api/admin/mantenimientos/mant-999", headers=mock_auth.as_admin())
    assert resp.status_code == 404


# -------- Auto-generación --------

def test_resolver_reporte_rota_genera_mantenimiento(client, mock_auth):
    """Crear un reporte tipo rota, resolverlo, verificar mantenimiento auto."""
    # Crear reporte como profesor
    reporte = client.post(
        "/api/profesor/reportes",
        json={
            "tipo": "rota",
            "prioridad": "alta",
            "descripcion": "La máquina no enciende.",
            "maquina_id": "mq-001",
        },
        headers=mock_auth.as_profesor(),
    ).get_json()["data"]

    # Resolver como admin
    client.post(
        f"/api/profesor/admin/reportes/{reporte['id']}/resolver",
        json={"resolucion": "Se reemplazó el motor."},
        headers=mock_auth.as_admin(),
    )

    # Verificar mantenimiento auto-generado
    resp = client.get(
        "/api/admin/maquinas/mq-001/mantenimientos",
        headers=mock_auth.as_admin(),
    )
    data = resp.get_json()["data"]
    autos = [
        m for m in data["mantenimientos"]
        if m["origen"] == "auto" and m["reporte_id"] == reporte["id"]
    ]
    assert len(autos) == 1
    assert autos[0]["tipo"] == "correctivo"


def test_resolver_reporte_limpieza_no_genera(client, mock_auth):
    """Un reporte de limpieza no genera mantenimiento automático."""
    reporte = client.post(
        "/api/profesor/reportes",
        json={
            "tipo": "limpieza",
            "prioridad": "baja",
            "descripcion": "La máquina está sucia.",
            "maquina_id": "mq-002",
        },
        headers=mock_auth.as_profesor(),
    ).get_json()["data"]

    client.post(
        f"/api/profesor/admin/reportes/{reporte['id']}/resolver",
        json={"resolucion": "Se limpió."},
        headers=mock_auth.as_admin(),
    )

    resp = client.get(
        "/api/admin/maquinas/mq-002/mantenimientos",
        headers=mock_auth.as_admin(),
    )
    data = resp.get_json()["data"]
    autos = [
        m for m in data["mantenimientos"]
        if m["origen"] == "auto" and m["reporte_id"] == reporte["id"]
    ]
    assert len(autos) == 0