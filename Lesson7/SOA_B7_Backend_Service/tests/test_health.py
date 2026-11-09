def test_liveness_and_readiness(client):
    live = client.get("/healthz")
    assert live.status_code == 200
    assert live.get_json() == {"status": "ok"}
    ready = client.get("/ready")
    assert ready.status_code == 200
    assert ready.get_json()["checks"]["database"] == "ok"
