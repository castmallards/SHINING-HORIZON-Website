def test_health_returns_ok(client):


    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()
    assert "status" in body
    assert body["status"] == "healthy"