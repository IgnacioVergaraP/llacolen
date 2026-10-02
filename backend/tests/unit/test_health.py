def test_healthcheck(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["data"]["status"] == "ok"