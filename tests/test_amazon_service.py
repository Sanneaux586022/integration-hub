import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from app.services.amazon_tracking_service import AmazonApiclient, AmazonRepository


API_URL = "https://fake-axesso.example.com"
API_KEY = "fake-key-0000"


def _make_success_response(products=None, asins=None):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "searchProductDetails": products or [],
        "foundProducts": asins or [],
    }
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


def _make_http_error(status_code: int):
    err_resp = MagicMock()
    err_resp.status_code = status_code
    return httpx.HTTPStatusError(
        f"{status_code} Error", request=MagicMock(), response=err_resp
    )


def _mock_http(side_effect=None, return_value=None):
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    if side_effect:
        mock_client.get = AsyncMock(side_effect=side_effect)
    else:
        mock_client.get = AsyncMock(return_value=return_value)
    return mock_client


# --- AmazonApiclient.fetch_from_api ---

async def test_fetch_from_api_success():
    products = [{"asin": "B001TEST", "price": "29.99", "productDescription": "Mouse"}]
    asins = ["B001TEST"]
    mock_http = _mock_http(return_value=_make_success_response(products, asins))

    with patch("app.services.amazon_tracking_service.httpx.AsyncClient", return_value=mock_http):
        result_products, result_asins = await AmazonApiclient(API_URL, API_KEY).fetch_from_api("mouse")

    assert len(result_products) == 1
    assert result_products[0]["asin"] == "B001TEST"
    assert "B001TEST" in result_asins


async def test_fetch_from_api_retries_on_429():
    call_count = 0

    async def flaky_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise _make_http_error(429)
        return _make_success_response()

    mock_http = _mock_http(side_effect=flaky_get)
    with patch("app.services.amazon_tracking_service.httpx.AsyncClient", return_value=mock_http), \
         patch("app.services.amazon_tracking_service.asyncio.sleep", new_callable=AsyncMock):
        await AmazonApiclient(API_URL, API_KEY).fetch_from_api("keyword")

    assert call_count == 2


async def test_fetch_from_api_retries_on_503():
    call_count = 0

    async def flaky_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise _make_http_error(503)
        return _make_success_response()

    mock_http = _mock_http(side_effect=flaky_get)
    with patch("app.services.amazon_tracking_service.httpx.AsyncClient", return_value=mock_http), \
         patch("app.services.amazon_tracking_service.asyncio.sleep", new_callable=AsyncMock):
        await AmazonApiclient(API_URL, API_KEY).fetch_from_api("keyword")

    assert call_count == 3


async def test_fetch_from_api_raises_after_max_retries():
    mock_http = _mock_http(side_effect=_make_http_error(503))
    with patch("app.services.amazon_tracking_service.httpx.AsyncClient", return_value=mock_http), \
         patch("app.services.amazon_tracking_service.asyncio.sleep", new_callable=AsyncMock):
        with pytest.raises(RuntimeError, match="API non disponibile"):
            await AmazonApiclient(API_URL, API_KEY).fetch_from_api("keyword")


async def test_fetch_from_api_non_retryable_error_propagates():
    mock_http = _mock_http(side_effect=_make_http_error(403))
    with patch("app.services.amazon_tracking_service.httpx.AsyncClient", return_value=mock_http):
        with pytest.raises(httpx.HTTPStatusError):
            await AmazonApiclient(API_URL, API_KEY).fetch_from_api("keyword")


# --- AmazonRepository ---

async def test_repo_crea_articolo(db_session):
    repo = AmazonRepository(db_session)
    articolo = await repo.crea_articolo("B00TEST123", "Prodotto di Test")
    await db_session.commit()

    assert articolo.id is not None
    assert articolo.asin == "B00TEST123"
    assert articolo.titolo == "Prodotto di Test"


async def test_repo_inserisci_ricerca(db_session):
    repo = AmazonRepository(db_session)
    ricerca = await repo.inserisci_ricerca("Laptop Gaming")
    await db_session.commit()

    assert ricerca.id is not None
    assert ricerca.keyword == "laptop gaming"


async def test_repo_get_articoli_esistenti_empty(db_session):
    repo = AmazonRepository(db_session)
    result = await repo.get_articoli_esistenti(["ASIN1", "ASIN2"])
    assert result == {}


async def test_repo_get_articoli_esistenti_with_data(db_session):
    repo = AmazonRepository(db_session)
    await repo.crea_articolo("FOUND001", "Articolo Trovabile")
    await db_session.commit()

    result = await repo.get_articoli_esistenti(["FOUND001", "NOTFOUND"])
    assert "FOUND001" in result
    assert "NOTFOUND" not in result
    assert result["FOUND001"].titolo == "Articolo Trovabile"


async def test_repo_get_articoli_esistenti_partial_match(db_session):
    repo = AmazonRepository(db_session)
    await repo.crea_articolo("ASIN_A", "Prodotto A")
    await repo.crea_articolo("ASIN_B", "Prodotto B")
    await db_session.commit()

    result = await repo.get_articoli_esistenti(["ASIN_A", "ASIN_C"])
    assert len(result) == 1
    assert "ASIN_A" in result
