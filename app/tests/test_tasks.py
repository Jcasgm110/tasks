def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_create_and_list(client):
    resp = client.post("/tasks", json={"title": "aprender pytest"})
    assert resp.status_code == 201
    assert resp.get_json()["title"] == "aprender pytest"
    titles = [t["title"] for t in client.get("/tasks").get_json()]
    assert titles == ["aprender pytest"]


def test_create_without_title(client):
    resp = client.post("/tasks", json={})
    assert resp.status_code == 400


def test_delete(client):
    created = client.post("/tasks", json={"title": "x"}).get_json()
    resp = client.delete(f"/tasks/{created['id']}")
    assert resp.status_code == 204
    assert client.get("/tasks").get_json() == []


def test_delete_missing(client):
    assert client.delete("/tasks/999").status_code == 404


def test_sql_injection_is_just_text(client):
    evil = "x'); DROP TABLE tasks; --"
    resp = client.post("/tasks", json={"title": evil})
    assert resp.status_code == 201
    titles = [t["title"] for t in client.get("/tasks").get_json()]
    assert titles == [evil]