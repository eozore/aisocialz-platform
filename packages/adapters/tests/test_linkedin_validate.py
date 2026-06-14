"""Testes de validação do adapter LinkedIn."""

from adapters.base import PublishPayload
from adapters.credentials import CredentialResolver
from adapters.linkedin import LinkedInAdapter
from core_domain import Canal, Scope


def _make_payload(**kwargs) -> PublishPayload:
    defaults = {
        "scope": Scope(tenant_id="victor", brand_id="eozore"),
        "canal": Canal.LINKEDIN,
        "content_id": "content-1",
        "slot_id": "slot-1",
        "texto": "Post de teste no LinkedIn",
        "midias": [],
        "meta": {},
        "idempotency_key": "key-1",
    }
    defaults.update(kwargs)
    return PublishPayload(**defaults)


def test_li_text_within_limit() -> None:
    adapter = LinkedInAdapter(CredentialResolver())
    payload = _make_payload(texto="A" * 3000)
    issues = adapter.validate(payload)
    assert issues == []


def test_li_text_exceeds_limit() -> None:
    adapter = LinkedInAdapter(CredentialResolver())
    payload = _make_payload(texto="A" * 3001)
    issues = adapter.validate(payload)
    assert len(issues) == 1
    assert "3000" in issues[0].problema


def test_li_article_longer_limit() -> None:
    adapter = LinkedInAdapter(CredentialResolver())
    payload = _make_payload(
        texto="A" * 5000,
        meta={"formato": "artigo"},
    )
    issues = adapter.validate(payload)
    # Artigos têm limite de 120k, então 5k deve passar
    assert issues == []
