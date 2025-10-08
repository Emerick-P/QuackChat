import pytest

from app.schemas.duck import DuckPatch

@pytest.mark.anyio
async def test_get_and_patch_duck(client, auth_token):
    # GET
    r = await client.get("/me/duck", headers={"Authorization": f"Bearer {auth_token}"})
    assert r.status_code == 200
    duck = r.json().get("duck")
    assert "duck_color" in duck

    # PATCH
    new_color = "#FFC93A"
    body: DuckPatch = {"duck_color": new_color}
    r2 = await client.patch(
        "/me/duck",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=body,
    )
    assert r2.status_code == 200
    duck2 = r2.json().get("duck")
    assert duck2["duck_color"] == new_color