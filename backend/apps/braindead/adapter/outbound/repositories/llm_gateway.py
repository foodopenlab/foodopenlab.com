
from matrix.grid_exaone_llm_manager import chat as exaone_chat

from braindead.app.ports.output.llm_port import ILLMPort


class BraindeadLLMGateway(ILLMPort):
    def __init__(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt

    async def chat(self, message: str) -> str:
        return await exaone_chat(
            [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message},
            ]
        )
