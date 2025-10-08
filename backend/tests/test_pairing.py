import pytest

@pytest.mark.anyio
async def test_pairing_flow(client, auth_token):
    # create
    r = await client.post(
        "/pairing",
        data={"color": "#3B82F6"}
        )
    assert r.status_code == 200
    data = r.json()
    code = data["code"]
    assert data["expires_in"] is not None

    # claim
    r2 = await client.post(
        "/pairing/claim",
        data={"code": code, "twitch_user_id": "test_user_id"}
        )
    assert r2.status_code == 200
    claimed = r2.json()
    assert claimed["ok"] is True