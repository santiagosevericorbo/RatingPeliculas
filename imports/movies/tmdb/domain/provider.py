from dataclasses import dataclass
from datetime import datetime


@dataclass
class Provider:

    tmdb_id: int
    country: str
    provider_id: int
    provider_name: str
    logo_path: str
    type: str
    last_update: datetime
