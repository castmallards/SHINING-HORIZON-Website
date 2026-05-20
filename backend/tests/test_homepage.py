def test_homepage_returns_ok(client):

    response = client.get("/")

    assert response.status_code == 200

    # TODO: add more specific assertions (HTML content, key words like band names, category names, hero text, etc.)
    assert "text/html" in response.headers.get("content-type", "")

    assert "Shining Horizon Trading" in response.text
    


