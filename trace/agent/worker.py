import time
import asyncio
from shared.kafka_util import get_consumer, get_producer
from probes.http_probe import HttpProbe
from probes.https_probe import HttpsProbe

consumer = get_consumer("http_test_requests", "http-test-worker")
producer = get_producer()
loop = asyncio.get_event_loop()

probe_map = {
    "http": HttpProbe(),
    "https": HttpsProbe(),
}

print("Worker started...")

for msg in consumer:
    job = msg.value
    job_type = job.get("type", "http")
    probe = probe_map.get(job_type)

    if not probe:
        print(f"Unknown probe type: {job_type}")
        continue

    result = {
        "url": job.get("url"),
        "method": job.get("method", "GET"),
        "type": job_type,
    }

    try:
        result.update(loop.run_until_complete(probe.run(job)))
    except Exception as e:
        result.update({
            "status_code": 0,
            "elapsed_ms": 0.0,
            "success": False,
            "error": f"Probe failed: {str(e)}"
        })

    producer.send("http_test_results", result)
    print(f"Finished {job_type.upper()} test for {result['url']} - Success: {result['success']}")
