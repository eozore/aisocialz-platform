"""Testes do Google Analytics client (modo stub)."""

import pytest

from adapters.google_analytics import GAReport, GoogleAnalyticsClient


@pytest.mark.asyncio
async def test_ga_stub_returns_empty_report() -> None:
    """Sem client real, retorna relatório vazio (modo desenvolvimento)."""
    ga = GoogleAnalyticsClient(analytics_client=None)
    report = await ga.get_page_metrics(
        property_id="properties/123456789",
        days_back=7,
    )
    assert isinstance(report, GAReport)
    assert report.property_id == "properties/123456789"
    assert report.paginas == []
    assert report.total_views == 0


@pytest.mark.asyncio
async def test_ga_stub_traffic_sources_empty() -> None:
    """Sem client real, retorna dict vazio."""
    ga = GoogleAnalyticsClient(analytics_client=None)
    sources = await ga.get_traffic_sources(
        property_id="properties/123456789",
        days_back=7,
    )
    assert sources == {}


@pytest.mark.asyncio
async def test_ga_with_page_filter() -> None:
    """Pode filtrar por paths específicos (stub retorna vazio)."""
    ga = GoogleAnalyticsClient(analytics_client=None)
    report = await ga.get_page_metrics(
        property_id="properties/123456789",
        page_paths=["/blog/variaveis-aleatorias"],
        days_back=30,
    )
    assert report.periodo_inicio  # tem data
    assert report.periodo_fim
