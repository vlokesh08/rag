from app.core.security import (
    hash_password,
    hash_session_token,
    verify_password,
)


def test_hash_password_round_trips() -> None:
    hashed = hash_password("supersecret1")
    assert hashed != "supersecret1"
    assert verify_password("supersecret1", hashed)


def test_verify_password_rejects_wrong_password() -> None:
    hashed = hash_password("supersecret1")
    assert not verify_password("wrong-password", hashed)


def test_hash_session_token_is_deterministic() -> None:
    assert hash_session_token("abc") == hash_session_token("abc")
    assert hash_session_token("abc") != hash_session_token("xyz")
