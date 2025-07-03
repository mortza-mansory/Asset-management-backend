from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class AssetLocationEntity:
    id: Optional[int]
    asset_id: int
    latitude: float
    longitude: float
    geofence_radius: Optional[float]
    updated_at: datetime