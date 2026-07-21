from __future__ import annotations

import logging
from typing import Any

from titanic.app.dtos.crew_smith_captain_dto import ChatCommand, ChatResponse, SmithCaptainQuery, SmithCaptainResponse
from titanic.app.ports.input.crew_andrews_architect_use_case import AndrewsArchitectUseCase
from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.ports.input.crew_lowe_boat_use_case import LoweBoatUseCase
from titanic.app.ports.input.crew_smith_captain_use_case import SmithCaptainUseCase
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterRoasterUseCase
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTesterUseCase
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase

logger = logging.getLogger(__name__)


class SmithCaptainInteractor(SmithCaptainUseCase):
    """타이타닉 ML 파이프라인 프록시(오케스트레이터).

    각 캐릭터 use case에 위임만 하고, 자체 전처리·학습·LLM 로직은 갖지 않습니다.
    """

    def __init__(
        self,
        repository: Any,
        andrews: AndrewsArchitectUseCase,
        jack: JackTrainerUseCase,
        rose: RoseModelUseCase,
        cal: CalTesterUseCase,
        walter: WalterRoasterUseCase,
        lowe: LoweBoatUseCase,
        hartley: HartleyViolinUseCase,
    ) -> None:
        self.repository = repository
        self.andrews = andrews
        self.jack = jack
        self.rose = rose
        self.cal = cal
        self.walter = walter
        self.lowe = lowe
        self.hartley = hartley

    async def introduce_myself(self, query: SmithCaptainQuery) -> SmithCaptainResponse:
        return await self.repository.introduce_myself(query)

    async def chat(self, command: ChatCommand) -> ChatResponse:
        user_messages = [m.text for m in command.messages if m.role == "user" and m.text.strip()]
        message = user_messages[-1].strip() if user_messages else ""

        logger.info("[SmithCaptainInteractor] chat | message=%r", message)

        train_set = await self.walter.get_train_set()
        await self.walter.get_test_set()
        train_stats = await self.walter.get_train_stats()

        x_all, y_all = self.lowe.feature_engineering(train_set)
        trained = await self.jack.train_model(x_all, y_all)
        scores = await self.cal.test_model(trained)
        await self.hartley.get_correlation_heatmap()

        text = await self.andrews.compose_chat_reply(
            message,
            train_set=train_set,
            train_stats=train_stats,
            trained=trained,
            scores=scores,
        )
        return ChatResponse(text=text)
