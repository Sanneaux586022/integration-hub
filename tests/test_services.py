import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.weather_service import weatherService
from app.services.exchange_service import exchangeService
from app.services.news_service import newsService


def _mock_http_client(json_data: dict) -> AsyncMock:
    """Helper: costruisce un AsyncClient mockato che risponde con json_data."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = json_data
    mock_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.get = AsyncMock(return_value=mock_resp)
    return mock_client


# --- WeatherService ---

async def test_weather_service_saves_record(db_session):
    mock_http = _mock_http_client({
        "name": "Verona",
        "main": {"temp": 18.5},
        "weather": [{"description": "nuvoloso"}],
    })
    with patch("app.services.weather_service.httpx.AsyncClient", return_value=mock_http):
        record = await weatherService(db_session).get_and_save_weather("Verona")

    assert record.id is not None
    assert record.city == "Verona"
    assert record.temperature == 18.5
    assert record.description == "nuvoloso"


async def test_weather_service_raises_on_http_error(db_session):
    import httpx

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    err_resp = MagicMock()
    err_resp.status_code = 404
    mock_client.get = AsyncMock(
        side_effect=httpx.HTTPStatusError("404", request=MagicMock(), response=err_resp)
    )
    with patch("app.services.weather_service.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(httpx.HTTPStatusError):
            await weatherService(db_session).get_and_save_weather("CittaFalsa")


# --- ExchangeService ---

async def test_exchange_service_saves_record(db_session):
    mock_http = _mock_http_client({"conversion_rates": {"USD": 1.08}})
    with patch("app.services.exchange_service.httpx.AsyncClient", return_value=mock_http):
        record = await exchangeService(db_session).get_and_save_rate("EUR", "USD")

    assert record.id is not None
    assert record.base_currency == "EUR"
    assert record.target_currency == "USD"
    assert record.rate == 1.08


async def test_exchange_service_missing_target_raises(db_session):
    mock_http = _mock_http_client({"conversion_rates": {}})
    with patch("app.services.exchange_service.httpx.AsyncClient", return_value=mock_http):
        with pytest.raises(ValueError, match="non trovato"):
            await exchangeService(db_session).get_and_save_rate("EUR", "XYZ")


# --- NewsService ---

async def test_news_service_saves_articles(db_session):
    mock_http = _mock_http_client({
        "articles": [
            {
                "source": {"name": "TechCrunch"},
                "title": "AI avanza rapidamente",
                "url": "https://techcrunch.com/ai",
                "publishedAt": "2026-04-20T10:00:00Z",
            },
            {
                "source": {"name": "Wired"},
                "title": "Il futuro del web",
                "url": "https://wired.com/web",
                "publishedAt": "2026-04-19T08:00:00Z",
            },
        ]
    })
    with patch("app.services.news_service.httpx.AsyncClient", return_value=mock_http):
        articles = await newsService(db_session).fetch_and_save_news("tecnologia")

    assert len(articles) == 2
    assert articles[0].title == "AI avanza rapidamente"
    assert articles[0].source == "TechCrunch"
    assert articles[1].source == "Wired"


async def test_news_service_truncates_to_5_articles(db_session):
    raw_articles = [
        {
            "source": {"name": f"Source{i}"},
            "title": f"Titolo {i}",
            "url": f"https://example.com/{i}",
            "publishedAt": "2026-04-20T10:00:00Z",
        }
        for i in range(10)
    ]
    mock_http = _mock_http_client({"articles": raw_articles})
    with patch("app.services.news_service.httpx.AsyncClient", return_value=mock_http):
        articles = await newsService(db_session).fetch_and_save_news("test")

    assert len(articles) == 5


async def test_news_service_handles_empty_response(db_session):
    mock_http = _mock_http_client({"articles": []})
    with patch("app.services.news_service.httpx.AsyncClient", return_value=mock_http):
        articles = await newsService(db_session).fetch_and_save_news("niente")

    assert articles == []
