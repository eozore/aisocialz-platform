"""Registry de adapters — resolve adapter por canal, respeita team_subscriptions (doc 09 §3).

Um time inativo é invisível — registry recusa entregar adapter.
"""

from adapters.base import ChannelAdapter
from adapters.blog import BlogAdapter
from adapters.credentials import CredentialResolver
from adapters.linkedin import LinkedInAdapter
from adapters.meta import MetaFacebookAdapter, MetaInstagramAdapter, MetaThreadsAdapter
from core_domain import Canal, TeamId, TeamInactiveError

# Mapeamento canal -> team_id (doc 09 §3)
CANAL_TO_TEAM: dict[Canal, TeamId] = {
    Canal.LINKEDIN: TeamId.LINKEDIN,
    Canal.INSTAGRAM: TeamId.META,
    Canal.FACEBOOK: TeamId.META,
    Canal.THREADS: TeamId.META,
    Canal.BLOG: TeamId.BLOG,
    Canal.YOUTUBE: TeamId.YOUTUBE,
    Canal.TIKTOK: TeamId.TIKTOK,
}


class AdapterRegistry:
    """Resolve o adapter correto para um canal, checando team_subscriptions."""

    def __init__(
        self,
        credential_resolver: CredentialResolver,
        active_teams: set[str] | None = None,
    ) -> None:
        self._creds = credential_resolver
        self._active_teams = active_teams or set()

        # Registra adapters disponíveis
        self._adapters: dict[Canal, ChannelAdapter] = {
            Canal.INSTAGRAM: MetaInstagramAdapter(credential_resolver),
            Canal.THREADS: MetaThreadsAdapter(credential_resolver),
            Canal.FACEBOOK: MetaFacebookAdapter(credential_resolver),
            Canal.LINKEDIN: LinkedInAdapter(credential_resolver),
            Canal.BLOG: BlogAdapter(credential_resolver),
        }

    def get_adapter(self, canal: Canal) -> ChannelAdapter:
        """Retorna o adapter para o canal, ou levanta TeamInactiveError."""
        team = CANAL_TO_TEAM.get(canal)
        if team and team.value not in self._active_teams:
            raise TeamInactiveError(team.value)

        adapter = self._adapters.get(canal)
        if adapter is None:
            raise NotImplementedError(f"Adapter para canal '{canal}' não implementado ainda")
        return adapter

    def available_canals(self) -> list[Canal]:
        """Lista canais com adapter implementado E time ativo."""
        result: list[Canal] = []
        for canal in self._adapters:
            team = CANAL_TO_TEAM.get(canal)
            if team is None or team.value in self._active_teams:
                result.append(canal)
        return result
