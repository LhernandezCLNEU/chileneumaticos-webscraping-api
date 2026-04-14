import pytest


@pytest.mark.asyncio
async def test_title_formats_crud(client):
    # create
    payload = {"name": "tf1", "pattern": "(?P<brand>\\w+)", "example": "Pirelli X", "priority": 5}
    r = await client.post("/api/v1/title-formats", json=payload)
    assert r.status_code == 200
    data = r.json()
    tf_id = data["id"]
    assert data["name"] == "tf1"

    # list
    r = await client.get("/api/v1/title-formats")
    assert r.status_code == 200
    items = r.json()
    assert any(i["id"] == tf_id for i in items)

    # get
    r = await client.get(f"/api/v1/title-formats/{tf_id}")
    assert r.status_code == 200
    assert r.json()["id"] == tf_id

    # update
    r = await client.put(f"/api/v1/title-formats/{tf_id}", json={"priority": 10})
    assert r.status_code == 200
    assert r.json()["priority"] == 10

    # delete (soft disable)
    r = await client.delete(f"/api/v1/title-formats/{tf_id}")
    assert r.status_code == 200
    assert r.json().get("ok") is True
