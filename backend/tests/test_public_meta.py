def test_sitemap_is_xml(client):
    response = client.get("/sitemap.xml")

    assert response.status_code == 200
    assert "xml" in response.headers.get("content-type", "").lower()
    assert "<urlset" in response.text
    assert "<url>" in response.text
    assert "<loc>" in response.text
    assert "<priority>" in response.text
    assert "</urlset>" in response.text
    assert "</url>" in response.text
    assert "</loc>" in response.text
    assert "</priority>" in response.text


def test_robots_has_sitemap_line(client):
    response = client.get("/robots.txt")

    assert response.status_code == 200
    assert "Sitemap:" in response.text
    assert "/sitemap.xml" in response.text