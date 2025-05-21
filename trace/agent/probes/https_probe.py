import socket
import ssl
import time
from urllib.parse import urlparse
from probes.base import Probe

class HttpsProbe(Probe):
    async def run(self, job: dict) -> dict:
        url = job.get("url")
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or 443

        result = {
            "protocol": "https",
            "url": url,
            "dns_ok": False,
            "tcp_ok": False,
            "ssl_ok": False,
            "send_ok": False,
            "recv_ok": False,
            "status_code": 0,
            "elapsed_ms": 0,
            "success": False,
            "error": None
        }

        errors = []
        sock = None
        ssl_sock = None
        start_time = time.time()

        try:
            # DNS
            try:
                ip = socket.gethostbyname(host)
                result["dns_ok"] = True
            except Exception as e:
                errors.append(f"DNS: {e}")

            # TCP
            if result["dns_ok"]:
                try:
                    sock = socket.create_connection((ip, port), timeout=5)
                    result["tcp_ok"] = True
                except Exception as e:
                    errors.append(f"TCP: {e}")

            # SSL
            if result["tcp_ok"]:
                try:
                    context = ssl.create_default_context()
                    ssl_sock = context.wrap_socket(sock, server_hostname=host)
                    result["ssl_ok"] = True
                except ssl.SSLCertVerificationError as e:
                    result["ssl_ok"] = False
                    result["ssl_cert_error"] = str(e)

                    # Optionally: retry with unverified context to continue the request
                    try:
                        context = ssl._create_unverified_context()
                        ssl_sock = context.wrap_socket(sock, server_hostname=host)
                    except Exception as e2:
                        result["error"] = f"SSL fallback failed: {e2}"
                        return result

            # Send
            if ssl_sock:
                try:
                    request = f"GET {parsed.path or '/'} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                    ssl_sock.sendall(request.encode())
                    result["send_ok"] = True
                except Exception as e:
                    errors.append(f"Send: {e}")

            # Receive
            if ssl_sock and result["send_ok"]:
                try:
                    response = b""
                    while True:
                        chunk = ssl_sock.recv(4096)
                        if not chunk:
                            break
                        response += chunk
                    result["recv_ok"] = True

                    # Parse HTTP status
                    status_line = response.split(b"\r\n", 1)[0]
                    if b" " in status_line:
                        result["status_code"] = int(status_line.split()[1])
                except Exception as e:
                    errors.append(f"Receive: {e}")

        finally:
            result["elapsed_ms"] = (time.time() - start_time) * 1000
            try:
                if ssl_sock:
                    ssl_sock.close()
                elif sock:
                    sock.close()
            except:
                pass

        result["success"] = result["status_code"] < 400 if result["status_code"] else False
        result["error"] = "; ".join(errors) if errors else None
        return result
