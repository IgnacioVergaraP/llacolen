def _login(client, email="alumno@gimnasio.com", password="alumno123"):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    return resp.get_json()["data"]["token"]


def _auth_headers(client):
    return {"Authorization": f"Bearer {_login(client)}"}


def test_listar_sin_token(client):
    resp = client.get("/api/maquinas")
    assert resp.status_code == 401


def test_listar_con_token(client):
    resp = client.get("/api/maquinas", headers=_auth_headers(client))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 8
    # Verificamos estructura de un item
    item = data[0]
    assert {"id", "nombre", "grupos_musculares", "descripcion", "video_url", "imagen_url"} <= set(item.keys())


def test_filtrar_por_musculo(client):
    resp = client.get("/api/maquinas?musculo=pecho", headers=_auth_headers(client))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data) > 0
    for m in data:
        assert "pecho" in [g.lower() for g in m["grupos_musculares"]]


def test_filtrar_musculo_inexistente(client):
    resp = client.get("/api/maquinas?musculo=noexiste", headers=_auth_headers(client))
    assert resp.status_code == 200
    assert resp.get_json()["data"] == []


def test_detalle_ok(client):
    resp = client.get("/api/maquinas/mq-001", headers=_auth_headers(client))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["id"] == "mq-001"
    assert data["nombre"]


def test_detalle_no_existe(client):
    resp = client.get("/api/maquinas/mq-999", headers=_auth_headers(client))
    assert resp.status_code == 404
    assert resp.get_json()["error"]["name"] == "NotFound"