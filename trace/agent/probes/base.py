from abc import ABC, abstractmethod

class Probe(ABC):
    @abstractmethod
    async def run(self, job: dict) -> dict:
        pass
