"""
Tests del blueprint maquinas.

Todos usan mock_auth para autenticarse (sin llamadas a Supabase).
"""


def test_listar_sin_token(client):
    resp = client.get("/api/maquinas")
    assert resp.status_code == 401


def test_listar_con_token(client, mock_auth):
    resp = client.get("/api/maquinas", headers=mock_auth.as_alumno())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 8
    item = data[0]
    assert {"id", "nombre", "grupos_musculares", "descripcion", "video_url", "imagen_url"} <= set(item.keys())


def test_filtrar_por_musculo(client, mock_auth):
    resp = client.get("/api/maquinas?musculo=pecho", headers=mock_auth.as_alumno())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data) > 0
    for m in data:
        assert "pecho" in [g.lower() for g in m["grupos_musculares"]]


def test_filtrar_musculo_inexistente(client, mock_auth):
    resp = client.get("/api/maquinas?musculo=noexiste", headers=mock_auth.as_alumno())
    assert resp.status_code == 200
    assert resp.get_json()["data"] == []


def test_detalle_ok(client, mock_auth):
    resp = client.get("/api/maquinas/mq-001", headers=mock_auth.as_alumno())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["id"] == "mq-001"
    assert data["nombre"]


def test_detalle_no_existe(client, mock_auth):
    resp = client.get("/api/maquinas/mq-999", headers=mock_auth.as_alumno())
    assert resp.status_code == 404
    assert resp.get_json()["error"]["name"] == "NotFound"