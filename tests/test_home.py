def test_home_page_is_available(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.content == b"TeamRetroLoop is running."
