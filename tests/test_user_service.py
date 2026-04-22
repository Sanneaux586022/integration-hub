import pytest
from fastapi import HTTPException

from app.services.user_service import userService
from app.schemas.users import UserCreate


async def _seed_user(db_session, email="seed@example.com", username="seed", password="pass123"):
    return await userService(db_session).create_user(
        UserCreate(email=email, username=username, password=password)
    )


# --- create_user ---

async def test_create_user_success(db_session):
    svc = userService(db_session)
    user = await svc.create_user(UserCreate(email="nuovo@example.com", username="nuovo", password="secret"))

    assert user.id is not None
    assert user.email == "nuovo@example.com"
    assert user.username == "nuovo"
    assert user.hashed_password != "secret"


async def test_create_user_email_stored_lowercase(db_session):
    svc = userService(db_session)
    user = await svc.create_user(UserCreate(email="Upper@Example.COM", username="up", password="pass"))
    assert user.email == "upper@example.com"


async def test_create_user_duplicate_email_raises_400(db_session):
    await _seed_user(db_session, email="dup@example.com")
    with pytest.raises(HTTPException) as exc:
        await _seed_user(db_session, email="dup@example.com", username="altro")
    assert exc.value.status_code == 400


# --- get_user_by_email ---

async def test_get_user_by_email_found(db_session):
    await _seed_user(db_session, email="find@example.com")
    user = await userService(db_session).get_user_by_email("find@example.com")
    assert user is not None
    assert user.email == "find@example.com"


async def test_get_user_by_email_not_found(db_session):
    user = await userService(db_session).get_user_by_email("ghost@example.com")
    assert user is None


# --- authenticate_user ---

async def test_authenticate_user_success(db_session):
    await _seed_user(db_session, email="auth@example.com", password="correctpass")
    user = await userService(db_session).authenticate_user("auth@example.com", "correctpass")
    assert user.email == "auth@example.com"


async def test_authenticate_user_wrong_password_raises_400(db_session):
    await _seed_user(db_session, email="wp@example.com", password="correctpass")
    with pytest.raises(HTTPException) as exc:
        await userService(db_session).authenticate_user("wp@example.com", "wrongpass")
    assert exc.value.status_code == 400


async def test_authenticate_user_unknown_email_raises_400(db_session):
    with pytest.raises(HTTPException) as exc:
        await userService(db_session).authenticate_user("nobody@example.com", "any")
    assert exc.value.status_code == 400


async def test_authenticate_user_case_insensitive_email(db_session):
    await _seed_user(db_session, email="case@example.com", password="pass")
    user = await userService(db_session).authenticate_user("CASE@EXAMPLE.COM", "pass")
    assert user is not None
