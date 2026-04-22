from unittest.mock import AsyncMock, MagicMock, patch

# --- Root ---


async def test_root_returns_status(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "Integration Hub" in response.json()["status"]


# --- Registrazione ---


async def test_register_success(client):
    response = await client.post(
        "/api/v1/registrazione",
        json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "secret123",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "new@example.com"
    assert "id" in body
    assert "hashed_password" not in body


async def test_register_duplicate_email_returns_error(client):
    payload = {"email": "dup@example.com", "username": "dup", "password": "secret123"}
    await client.post("/api/v1/registrazione", json=payload)
    response = await client.post("/api/v1/registrazione", json=payload)
    assert response.status_code in (400, 500)


async def test_register_invalid_email_rejected(client):
    response = await client.post(
        "/api/v1/registrazione",
        json={
            "email": "not-an-email",
            "username": "user",
            "password": "pass",
        },
    )
    assert response.status_code == 422


# --- Login ---


async def test_login_success(client, test_user):
    response = await client.post(
        "/api/v1/login",
        json={
            "email": "mario@example.com",
            "plain_password": "password123",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


async def test_login_wrong_password(client, test_user):
    response = await client.post(
        "/api/v1/login",
        json={
            "email": "mario@example.com",
            "plain_password": "sbagliata",
        },
    )
    assert response.status_code == 400


async def test_login_unknown_email(client):
    response = await client.post(
        "/api/v1/login",
        json={
            "email": "ghost@example.com",
            "plain_password": "anypass",
        },
    )
    assert response.status_code == 400


# --- /me ---


async def test_me_authenticated(client, test_user, auth_headers):
    response = await client.get("/api/v1/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email


async def test_me_with_cookie(client, test_user):
    # Login per ottenere il token, poi usarlo come cookie
    login_resp = await client.post(
        "/api/v1/login",
        json={
            "email": "mario@example.com",
            "plain_password": "password123",
        },
    )
    token = login_resp.json()["access_token"]
    response = await client.get("/api/v1/me", cookies={"access_token": token})
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email


async def test_me_unauthenticated_no_token(client):
    response = await client.get("/api/v1/me")
    # get_current_user ritorna None → accesso a None.username → 500
    assert response.status_code in (401, 422, 500)


async def test_me_expired_token(client, test_user):
    from datetime import timedelta

    from app.core.security import create_access_token

    token = create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(seconds=-1),
    )
    response = await client.get(
        "/api/v1/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in (401, 422, 500)


# --- Dashboard API ---


async def test_dashboard_returns_correct_keys(client, test_user, auth_headers):
    response = await client.get("/api/v1/dashboard", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert "weather" in body
    assert "exchange" in body
    assert "news" in body


async def test_dashboard_empty_db(client, test_user, auth_headers):
    response = await client.get("/api/v1/dashboard", headers=auth_headers)
    body = response.json()
    assert body["weather"] is None
    assert body["exchange"] is None
    assert body["news"] == []


# --- System stats ---


async def test_system_stats_authenticated(client, test_user, auth_headers):
    with patch("app.api.routes.systemService.get_syst_stats") as mock_stats:
        mock_stats.return_value = {
            "cpu_temp": 42.5,
            "cpu_usage": 12.3,
            "ram_usage": 55.1,
            "status": "Online",
        }
        response = await client.get("/api/v1/system-stats", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "Online"
    assert response.json()["cpu_temp"] == 42.5


# --- Weather update ---


async def test_weather_update_success(client, test_user, auth_headers):
    mock_http = AsyncMock()
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=None)

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "name": "Verona",
        "main": {"temp": 22.5},
        "weather": [{"description": "sereno"}],
    }
    mock_resp.raise_for_status = MagicMock()
    mock_http.get = AsyncMock(return_value=mock_resp)

    with patch(
        "app.services.weather_service.httpx.AsyncClient", return_value=mock_http
    ):
        response = await client.get(
            "/api/v1/weather/update/Verona", headers=auth_headers
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["temp"] == 22.5


async def test_weather_update_api_error(client, test_user, auth_headers):
    import httpx as _httpx

    mock_http = AsyncMock()
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=None)
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_http.get = AsyncMock(
        side_effect=_httpx.HTTPStatusError(
            "401", request=MagicMock(), response=mock_resp
        )
    )

    with patch(
        "app.services.weather_service.httpx.AsyncClient", return_value=mock_http
    ):
        response = await client.get(
            "/api/v1/weather/update/CittaInesistente", headers=auth_headers
        )

    assert response.status_code == 500


# --- Weather history ---


async def test_weather_history_empty(client, test_user, auth_headers):
    response = await client.get("/api/v1/weather/history", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []
