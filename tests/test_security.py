import pytest
from datetime import timedelta
from jose import jwt, JWTError

from app.core.security import verify_password, get_password_hash, create_acces_token
from app.core.config import settings


def test_hash_is_different_from_plain():
    hashed = get_password_hash("mypassword")
    assert hashed != "mypassword"
    assert len(hashed) > 20


def test_bcrypt_salt_produces_different_hashes():
    """bcrypt usa salt casuale: stesso input → hash diversi."""
    h1 = get_password_hash("mypassword")
    h2 = get_password_hash("mypassword")
    assert h1 != h2


def test_verify_password_correct():
    hashed = get_password_hash("correctpass")
    assert verify_password("correctpass", hashed) is True


def test_verify_password_wrong():
    hashed = get_password_hash("correctpass")
    assert verify_password("wrongpass", hashed) is False


def test_verify_password_empty_string():
    hashed = get_password_hash("realpass")
    assert verify_password("", hashed) is False


def test_create_token_contains_sub():
    token = create_acces_token(data={"sub": "user@example.com"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "user@example.com"


def test_create_token_contains_exp():
    token = create_acces_token(data={"sub": "user@example.com"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert "exp" in payload


def test_create_token_custom_expiry():
    token = create_acces_token(
        data={"sub": "user@example.com"},
        expires_delta=timedelta(hours=2),
    )
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "user@example.com"


def test_create_token_default_expiry_is_15_min():
    """Senza expires_delta il fallback è 15 minuti."""
    import time
    before = int(time.time())
    token = create_acces_token(data={"sub": "u@e.com"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    after = int(time.time())
    expected_exp_low = before + 14 * 60
    expected_exp_high = after + 16 * 60
    assert expected_exp_low <= payload["exp"] <= expected_exp_high


def test_token_invalid_with_wrong_key():
    token = create_acces_token(data={"sub": "user@example.com"})
    with pytest.raises(JWTError):
        jwt.decode(token, "completamente-sbagliata", algorithms=[settings.ALGORITHM])


def test_token_invalid_algorithm():
    token = create_acces_token(data={"sub": "user@example.com"})
    with pytest.raises(JWTError):
        jwt.decode(token, settings.SECRET_KEY, algorithms=["RS256"])
