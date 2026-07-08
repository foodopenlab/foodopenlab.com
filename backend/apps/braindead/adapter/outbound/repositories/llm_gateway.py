
import os

import httpx

from braindead.app.ports.output.llm_port import ILLMPort

_DEFAULT_MODEL = "exaone3.5:2.4b"
_OLLAMA_URL = "http://host.docker.internal:11434/api/chat"


class BraindeadLLMGateway(ILLMPort):
    def __init__(self, system_prompt: str) -> None:
        self.model = os.getenv("BRAINDEAD_MODEL", _DEFAULT_MODEL)
        self.system_prompt = system_prompt

    async def chat(self, message: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message},
            ],
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(_OLLAMA_URL, json=payload)
            resp.raise_for_status()
        return resp.json()["message"]["content"]
