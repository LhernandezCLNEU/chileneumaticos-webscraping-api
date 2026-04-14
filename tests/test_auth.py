import pytest

from app.models.user import User
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_token_issue(client, db_session):
    # create user
    u = User(email="test@example.com", hashed_password=get_password_hash("secret"))
    db_session.add(u)
    await db_session.commit()
    await db_session.refresh(u)

    # request token
    data = {"username": "test@example.com", "password": "secret"}
    r = await client.post("/api/v1/auth/token", data=data)
    assert r.status_code == 200
    json = r.json()
    assert "access_token" in json
    assert json["token_type"] == "bearer"
