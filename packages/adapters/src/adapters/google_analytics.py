"""Google Analytics 4 — coleta de métricas web (modo coleta, Fase 1).

Usa a Google Analytics Data API (GA4) para buscar métricas de páginas
publicadas (blog, portfólio) e fechar o funil até os sites.

Credenciais: Application Default Credentials (a mesma SA do svc-agents).
Não precisa de secret separado — usa IAM do projeto.

Formato esperado na config da marca:
{
    "analytics_web": {
        "property_id": "properties/123456789",  # GA4 property ID
        "ativo": true
    }
}
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field


class GAPageMetrics(BaseModel):
    """Métricas de uma página específica coletadas do GA4."""

    page_path: str
    views: int = 0
    users: int = 0
    avg_engagement_time_sec: float = 0.0
    bounce_rate: float = 0.0
    conversions: int = 0  # eventos de conversão (ex: newsletter_signup)
    source_medium: str = ""  # de onde veio o tráfego


class GAReport(BaseModel):
    """Relatório de métricas do GA4 para um período."""

    property_id: str
    periodo_inicio: str
    periodo_fim: str
    paginas: list[GAPageMetrics] = Field(default_factory=list)
    total_users: int = 0
    total_views: int = 0
    coletado_em: str = ""


class GoogleAnalyticsClient:
    """Client para Google Analytics Data API (GA4).

    Fase 1: modo coleta — busca métricas, não configura nada no GA.
    """

    def __init__(self, analytics_client: Any | None = None) -> None:
        """
        Args:
            analytics_client: google.analytics.data_v1beta.BetaAnalyticsDataClient
                              Se None, opera em modo stub (para testes).
        """
        self._client = analytics_client

    async def get_page_metrics(
        self,
        property_id: str,
        page_paths: list[str] | None = None,
        days_back: int = 7,
    ) -> GAReport:
        """Busca métricas de páginas do GA4 nos últimos N dias.

        Args:
            property_id: ex "properties/123456789"
            page_paths: filtrar por paths específicos (ex: ["/blog/meu-post"])
            days_back: quantos dias para trás buscar
        """
        end_date = datetime.now(UTC).date()
        start_date = end_date - timedelta(days=days_back)

        if self._client is None:
            # Modo stub para testes
            return GAReport(
                property_id=property_id,
                periodo_inicio=start_date.isoformat(),
                periodo_fim=end_date.isoformat(),
                paginas=[],
                total_users=0,
                total_views=0,
                coletado_em=datetime.now(UTC).isoformat(),
            )

        # Chamada real à GA4 Data API
        from google.analytics.data_v1beta import RunReportRequest

        dimensions = [
            {"name": "pagePath"},
            {"name": "sessionSourceMedium"},
        ]
        metrics = [
            {"name": "screenPageViews"},
            {"name": "totalUsers"},
            {"name": "averageSessionDuration"},
            {"name": "bounceRate"},
            {"name": "conversions"},
        ]

        request = RunReportRequest(
            property=property_id,
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[
                {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                }
            ],
        )

        # Filtro por paths específicos se fornecido
        if page_paths:
            request.dimension_filter = {
                "filter": {
                    "field_name": "pagePath",
                    "in_list_filter": {"values": page_paths},
                }
            }

        response = self._client.run_report(request)

        # Parse response
        paginas: list[GAPageMetrics] = []
        total_users = 0
        total_views = 0

        for row in response.rows:
            page_path = row.dimension_values[0].value
            source_medium = row.dimension_values[1].value
            views = int(row.metric_values[0].value)
            users = int(row.metric_values[1].value)
            avg_time = float(row.metric_values[2].value)
            bounce = float(row.metric_values[3].value)
            conversions = int(row.metric_values[4].value)

            paginas.append(
                GAPageMetrics(
                    page_path=page_path,
                    views=views,
                    users=users,
                    avg_engagement_time_sec=avg_time,
                    bounce_rate=bounce,
                    conversions=conversions,
                    source_medium=source_medium,
                )
            )
            total_users += users
            total_views += views

        return GAReport(
            property_id=property_id,
            periodo_inicio=start_date.isoformat(),
            periodo_fim=end_date.isoformat(),
            paginas=paginas,
            total_users=total_users,
            total_views=total_views,
            coletado_em=datetime.now(UTC).isoformat(),
        )

    async def get_traffic_sources(
        self,
        property_id: str,
        days_back: int = 7,
    ) -> dict[str, int]:
        """Resumo de fontes de tráfego (para atribuição canal → conversão).

        Retorna: {"instagram": 120, "linkedin": 85, "threads": 45, ...}
        """
        if self._client is None:
            return {}

        from google.analytics.data_v1beta import RunReportRequest

        request = RunReportRequest(
            property=property_id,
            dimensions=[{"name": "sessionSource"}],
            metrics=[{"name": "totalUsers"}],
            date_ranges=[
                {
                    "start_date": (
                        datetime.now(UTC).date() - timedelta(days=days_back)
                    ).isoformat(),
                    "end_date": datetime.now(UTC).date().isoformat(),
                }
            ],
        )

        response = self._client.run_report(request)
        sources: dict[str, int] = {}
        for row in response.rows:
            source = row.dimension_values[0].value.lower()
            users = int(row.metric_values[0].value)
            sources[source] = sources.get(source, 0) + users

        return sources
