from datetime import datetime, UTC
from domain.provider import Provider


class ProviderService:

    def parse_uy_providers(self, tmdb_id, data):

        uy = data.get("results", {}).get("UY")

        if not uy:
            return []

        providers = []

        for offer_type in ["flatrate", "rent", "buy"]:
            for p in uy.get(offer_type, []):

                providers.append(
                    Provider(
                        tmdb_id=tmdb_id,
                        country="UY",
                        provider_id=p["provider_id"],
                        provider_name=p["provider_name"],
                        logo_path=p["logo_path"],
                        type=offer_type,
                        last_update=datetime.now(UTC),
                    )
                )

        return providers
