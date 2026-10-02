"""
Tests del blueprint rutinas (vista alumno).
"""


def test_listar_sin_token(client):
    resp = client.get("/api/rutinas")
    assert resp.status_code == 401


def test_listar_como_alumno(client, mock_auth):
    resp = client.get("/api/rutinas", headers=mock_auth.as_alumno())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 3
    for r in data:
        assert {"id", "titulo", "grupos_musculares", "alumno_id", "ejercicios"} <= set(r.keys())


def test_listar_como_profesor_vacio(client, mock_auth):
    """El profesor no tiene rutinas mockeadas propias → array vacío."""
    resp = client.get("/api/rutinas", headers=mock_auth.as_profesor())
    assert resp.status_code == 200
    assert resp.get_json()["data"] == []


def test_detalle_ok(client, mock_auth):
    resp = client.get("/api/rutinas/rt-001", headers=mock_auth.as_alumno())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["id"] == "rt-001"
    assert len(data["ejercicios"]) == 4
    ej0 = data["ejercicios"][0]
    assert ej0["tipo"] == "maquina"
    assert ej0["maquina_id"] == "mq-004"
    assert ej0["maquina"] is not None
    assert "nombre" in ej0["maquina"]


def test_detalle_con_ejercicio_libre(client, mock_auth):
    resp = client.get("/api/rutinas/rt-003", headers=mock_auth.as_alumno())
    data = resp.get_json()["data"]
    libres = [e for e in data["ejercicios"] if e["tipo"] == "libre"]
    assert len(libres) == 2
    assert libres[0]["nombre"]
    assert "maquina" not in libres[0] or libres[0].get("maquina") is None


def test_detalle_rutina_ajena_404(client, mock_auth):
    """El profesor no es dueño de las rutinas → 404."""
    resp = client.get("/api/rutinas/rt-001", headers=mock_auth.as_profesor())
    assert resp.status_code == 404
    assert resp.get_json()["error"]["name"] == "NotFound"


def test_detalle_no_existe_404(client, mock_auth):
    resp = client.get("/api/rutinas/rt-999", headers=mock_auth.as_alumno())
    assert resp.status_code == 404