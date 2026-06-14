"""Testes de validação do adapter Blog."""

from adapters.base import PublishPayload
from adapters.blog import BlogAdapter
from adapters.credentials import CredentialResolver
from core_domain import Canal, Scope


def _make_payload(**kwargs) -> PublishPayload:
    defaults = {
        "scope": Scope(tenant_id="victor", brand_id="eozore"),
        "canal": Canal.BLOG,
        "content_id": "content-1",
        "slot_id": "slot-1",
        "texto": (
            "Este é um post de blog com conteúdo suficiente "
            "para passar na validação mínima de caracteres exigida pelo adapter."
        ),
        "midias": [],
        "meta": {"titulo": "Meu Post"},
        "idempotency_key": "key-1",
    }
    defaults.update(kwargs)
    return PublishPayload(**defaults)


def test_blog_valid_post() -> None:
    adapter = BlogAdapter(CredentialResolver())
    payload = _make_payload()
    issues = adapter.validate(payload)
    assert issues == []


def test_blog_title_too_long() -> None:
    adapter = BlogAdapter(CredentialResolver())
    payload = _make_payload(meta={"titulo": "A" * 201})
    issues = adapter.validate(payload)
    assert any("200" in i.problema for i in issues)


def test_blog_body_too_short() -> None:
    adapter = BlogAdapter(CredentialResolver())
    payload = _make_payload(texto="Curto")
    issues = adapter.validate(payload)
    assert any("100" in i.problema for i in issues)
