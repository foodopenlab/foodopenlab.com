from fastapi import Depends

from ontology.adapter.outbound.llm.gemini_command_interpreter_adapter import (
    GeminiCommandInterpreterAdapter,
)
from ontology.app.ports.input.crawler_use_case import ICrawlerUseCase
from ontology.app.ports.input.scout_use_case import IScoutUseCase
from ontology.app.ports.input.scraper_use_case import IScraperUseCase
from ontology.app.ports.output.command_interpreter_port import ICommandInterpreterPort
from ontology.app.ports.output.gemini_port import IGeminiPort
from ontology.app.use_cases.scout_interactor import ScoutInteractor
from ontology.dependencies.crawler_provider import get_crawler_use_case
from ontology.dependencies.gateway_provider import get_gemini_port
from ontology.dependencies.scraper_provider import get_scraper_use_case


def get_command_interpreter(
    gemini: IGeminiPort = Depends(get_gemini_port),
) -> ICommandInterpreterPort:
    return GeminiCommandInterpreterAdapter(gemini=gemini)


def get_scout_use_case(
    interpreter: ICommandInterpreterPort = Depends(get_command_interpreter),
    crawler: ICrawlerUseCase = Depends(get_crawler_use_case),
    scraper: IScraperUseCase = Depends(get_scraper_use_case),
) -> IScoutUseCase:
    return ScoutInteractor(interpreter=interpreter, crawler=crawler, scraper=scraper)
