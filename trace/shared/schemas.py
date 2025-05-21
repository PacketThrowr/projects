from pydantic import BaseModel, HttpUrl
from typing import Optional

class TestRequest(BaseModel):
    url: HttpUrl
    method: str = "GET"
    type: str = "http"

class TestResult(BaseModel):
    url: str
    method: str
    status_code: int
    elapsed_ms: float
    success: bool
    error: str | None = None
    timestamp: float | None = None
    dns_ok: Optional[bool] = None
    tcp_ok: Optional[bool] = None
    ssl_ok: Optional[bool] = None
    send_ok: Optional[bool] = None
    recv_ok: Optional[bool] = None
    protocol: Optional[str] = None
    ssl_cert_error: Optional[str] = None