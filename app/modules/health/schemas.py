from enum import Enum
from pydantic import BaseModel


class HealthStatus(str, Enum):
    OK = "ok"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class ComponentHealth(BaseModel):
    name: str
    status: HealthStatus
    detail: str | None = None


class HealthResponse(BaseModel):
    status: HealthStatus
    app_name: str
    version: str = "1.0.0"
    components: list[ComponentHealth]
