import time
import httpx
from probes.base import Probe

class HttpProbe(Probe):
    async def run(self, job: dict) -> dict:
        url = job.get("url")
        method = job.get("method", "GET")
        result = {
            "protocol": "http",
            "url": url,
            "method": method,
            "elapsed_ms": 0,
            "status_code": 0,
            "success": False,
            "error": None,
        }

        try:
            start = time.time()
            r = httpx.request(method, url, timeout=10)
            result["elapsed_ms"] = (time.time() - start) * 1000
            result["status_code"] = r.status_code
            result["success"] = r.status_code < 400
        except Exception as e:
            result["error"] = str(e)

        return result
