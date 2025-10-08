import pytest

@pytest.mark.anyio
async def test_login_and_me(client):
    r = await client.post("/auth/login", params={"display": "Liargo Test"})
    assert r.status_code == 200
    token = r.json()["access_token"]

    r2 = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    me = r2.json()
    assert me["display"] == "Liargo Test"
    assert "user_id" in me