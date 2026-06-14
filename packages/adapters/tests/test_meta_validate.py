"""Testes de validação dos adapters Meta — doc 01 §3.

validate() roda no agendamento, não na hora de postar.
"""

from adapters.base import PublishPayload
from adapters.credentials import CredentialResolver
from adapters.meta import MetaInstagramAdapter, MetaThreadsAdapter
from core_domain import Canal, Scope


def _make_payload(**kwargs) -> PublishPayload:
    defaults = {
        "scope": Scope(tenant_id="victor", brand_id="eozore"),
        "canal": Canal.INSTAGRAM,
        "content_id": "content-1",
        "slot_id": "slot-1",
        "texto": "Post de teste",
        "midias": ["gs://assets/img1.png"],
        "meta": {},
        "idempotency_key": "key-1",
    }
    defaults.update(kwargs)
    return PublishPayload(**defaults)


def test_ig_caption_within_limit() -> None:
    adapter = MetaInstagramAdapter(CredentialResolver())
    payload = _make_payload(texto="Texto curto")
    issues = adapter.validate(payload)
    assert issues == []


def test_ig_caption_exceeds_limit() -> None:
    adapter = MetaInstagramAdapter(CredentialResolver())
    payload = _make_payload(texto="A" * 2201)
    issues = adapter.validate(payload)
    assert len(issues) == 1
    assert "2200" in issues[0].problema


def test_ig_carousel_too_few_images() -> None:
    adapter = MetaInstagramAdapter(CredentialResolver())
    payload = _make_payload(
        midias=["gs://img1.png"],
        meta={"formato": "carrossel"},
    )
    issues = adapter.validate(payload)
    assert any("2-10" in i.problema for i in issues)


def test_ig_carousel_too_many_images() -> None:
    adapter = MetaInstagramAdapter(CredentialResolver())
    payload = _make_payload(
        midias=[f"gs://img{i}.png" for i in range(11)],
        meta={"formato": "carrossel"},
    )
    issues = adapter.validate(payload)
    assert any("2-10" in i.problema for i in issues)


def test_ig_too_many_hashtags() -> None:
    adapter = MetaInstagramAdapter(CredentialResolver())
    payload = _make_payload(texto="Post " + " ".join(f"#{i}" for i in range(31)))
    issues = adapter.validate(payload)
    assert any("hashtag" in i.problema.lower() for i in issues)


def test_threads_text_within_limit() -> None:
    adapter = MetaThreadsAdapter(CredentialResolver())
    payload = _make_payload(canal=Canal.THREADS, texto="Texto curto")
    issues = adapter.validate(payload)
    assert issues == []


def test_threads_text_exceeds_limit() -> None:
    adapter = MetaThreadsAdapter(CredentialResolver())
    payload = _make_payload(canal=Canal.THREADS, texto="A" * 501)
    issues = adapter.validate(payload)
    assert len(issues) == 1
    assert "500" in issues[0].problema
