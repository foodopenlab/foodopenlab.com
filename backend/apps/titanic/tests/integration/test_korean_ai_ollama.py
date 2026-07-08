"""Kiwi 전처리 + Ollama EEVE-Korean 연동 확인 (로컬 Ollama 필요)."""

from __future__ import annotations

from typing import cast

import pytest

pytest.importorskip("ollama")
pytest.importorskip("kiwipiepy")

import ollama
from kiwipiepy import Kiwi, Token

pytestmark = [pytest.mark.integration, pytest.mark.ollama]

_kiwi = Kiwi()
_DEFAULT_QUESTION = (
    "자연어처리는 넘흐 재밌어요. 올라마와 키위 라이브러리의 장점을 짧게 요약해줘."
)
_OLLAMA_MODEL = "anpigon/eeve-korean-10.8b:latest"


def run_korean_ai(user_text: str) -> str:
    cleaned_text = _kiwi.space(user_text)
    tokens = cast(list[Token], _kiwi.tokenize(str(cleaned_text)))
    nouns = [t.form for t in tokens if t.tag.startswith("NN")]

    assert nouns, "Kiwi 명사 추출 결과가 비어 있으면 안 됩니다."

    response = ollama.chat(
        model=_OLLAMA_MODEL,
        messages=[{"role": "user", "content": cleaned_text}],
    )
    content = response.message.content
    assert content is not None
    return content


@pytest.fixture(scope="module")
def ollama_ready() -> None:
    try:
        models = ollama.list()
    except Exception as exc:  # pragma: no cover - 환경 의존
        pytest.skip(f"Ollama 서버에 연결할 수 없습니다: {exc}")

    model_names = {m.model for m in models.models}
    if _OLLAMA_MODEL not in model_names:
        pytest.skip(f"Ollama 모델이 없습니다: {_OLLAMA_MODEL}")


def test_kiwi_preprocesses_korean_text() -> None:
    cleaned = _kiwi.space("자연어처리는넘흐재밌어요")
    tokens = cast(list[Token], _kiwi.tokenize(str(cleaned)))
    nouns = [t.form for t in tokens if t.tag.startswith("NN")]

    assert nouns
    assert any("자연어" in n or "처리" in n for n in nouns)


def test_run_korean_ai_returns_answer(ollama_ready: None) -> None:
    answer = run_korean_ai(_DEFAULT_QUESTION)

    assert isinstance(answer, str)
    assert answer.strip()


if __name__ == "__main__":
    print(run_korean_ai(_DEFAULT_QUESTION))
