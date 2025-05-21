from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from threading import Thread
from shared.kafka_util import get_producer, get_consumer
from shared.schemas import TestRequest, TestResult
import json, time

app = FastAPI()

result_cache = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/probe")
async def enqueue_test(req: TestRequest):
    producer = get_producer()
    producer.send("http_test_requests", json.loads(req.json()))
    return {"queued": True}

@app.get("/results", response_model=list[TestResult])
async def get_results():
    return list(reversed(result_cache))[:10]  # return last 10 results (most recent first)


def result_listener():
    consumer = get_consumer("http_test_results", "result-api")
    print("Result listener started...")
    for msg in consumer:
        try:
            result = msg.value
            result["timestamp"] = time.time()
            result_cache.append(result)
            if len(result_cache) > 100:
                result_cache.pop(0)  # keep memory usage low
        except Exception as e:
            print("Error parsing result:", e)


# Start Kafka listener thread when app starts
@app.on_event("startup")
def startup_event():
    Thread(target=result_listener, daemon=True).start()