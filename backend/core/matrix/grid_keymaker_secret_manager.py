"""시스템 전역 API 키·환경 변수·외부 클라이언트(Gemini 등)를 한곳에서 관리합니다."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from matrix.external_api_budget import consume_external_api_unit_or_raise

# Google AI Studio 권장 모델 (할당량 초과 시 아래 순서로 대체 시도)
# - gemini-2.5-flash-lite: 안정화·저비용 (기본)
# - gemini-2.5-flash: 2.5 Flash
# - gemini-3.1-flash-lite: 3세대 경량
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-lite"
FALLBACK_GEMINI_MODELS = (
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-3.1-flash-lite",
)


def default_backend_env_path() -> Path:
    """`com.auditor/.env` — 이 파일: `core/matrix/grid_keymaker_secret_manager.py` 기준."""
    return Path(__file__).resolve().parent.parent.parent / ".env"


class Keymaker:
    """
    전역 키·설정 관리자.

    - `com.auditor/.env` 로드
    - Gemini API 키 및 `google.genai.Client` 보관
    - 이후 다른 서비스 키도 동일 객체에서 확장 가능
    """

    _instance: Keymaker | None = None

    def __init__(self, env_path: Path | None = None) -> None:
        self._env_path = env_path or default_backend_env_path()
        self._dotenv_loaded = False
        self._gemini_client: Any = None
        self._gemini_model_id = DEFAULT_GEMINI_MODEL

    @classmethod
    def instance(cls, env_path: Path | None = None) -> Keymaker:
        """프로세스당 하나의 Keymaker (첫 생성 시 env_path만 적용)."""
        if cls._instance is None:
            cls._instance = cls(env_path=env_path)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """테스트 등에서 인스턴스를 비울 때만 사용."""
        cls._instance = None

    def load_env(self) -> None:
        """`.env`를 한 번만 로드하고, 등록된 클라이언트를 부트스트랩합니다."""
        if self._dotenv_loaded:
            return
        from dotenv import load_dotenv

        load_dotenv(self._env_path)
        self._dotenv_loaded = True
        self._bootstrap_gemini()

    def _bootstrap_gemini(self) -> None:
        try:
            from google import genai
        except ImportError:
            self._gemini_client = None
            return

        key = (os.getenv("GEMINI_API_KEY") or "").strip()
        if not key:
            self._gemini_client = None
            return
        model_id = self._normalize_model_id(os.getenv("GEMINI_MODEL") or self._gemini_model_id)
        self._gemini_model_id = model_id or DEFAULT_GEMINI_MODEL
        self._gemini_client = genai.Client(api_key=key)

    @staticmethod
    def _normalize_model_id(model_id: str) -> str:
        model_id = model_id.strip()
        if model_id.startswith("models/"):
            model_id = model_id.removeprefix("models/")
        return model_id

    @staticmethod
    def is_quota_error(exc: BaseException) -> bool:
        msg = str(exc).lower()
        if "429" in str(exc) or "quota" in msg or "rate limit" in msg:
            return True
        return type(exc).__name__ in ("ResourceExhausted", "TooManyRequests")

    def _models_to_try(self) -> list[str]:
        ordered: list[str] = [self._gemini_model_id]
        for mid in FALLBACK_GEMINI_MODELS:
            if mid not in ordered:
                ordered.append(mid)
        return ordered

    def generate_content(self, prompt: str) -> Any:
        """Gemini generate_content. 429(할당량)이면 대체 모델을 순서대로 시도합니다."""
        self.load_env()
        if not self.is_gemini_ready():
            raise RuntimeError("GEMINI_API_KEY가 설정되지 않았습니다.")
        consume_external_api_unit_or_raise(units=1, label="gemini.generate_content")

        client = self._gemini_client
        last_quota_error: BaseException | None = None
        for model_id in self._models_to_try():
            try:
                return client.models.generate_content(model=model_id, contents=prompt)
            except Exception as e:
                if self.is_quota_error(e):
                    last_quota_error = e
                    continue
                raise
        if last_quota_error is not None:
            raise last_quota_error
        raise RuntimeError("사용 가능한 Gemini 모델이 없습니다.")

    def get_secret(self, name: str, default: str = "") -> str:
        """임의 환경 변수(민감 값) 조회. 필요 시 `.env` 로드를 트리거합니다."""
        self.load_env()
        return (os.getenv(name) or default).strip()

    def get_gemini_api_key(self) -> str:
        self.load_env()
        return (os.getenv("GEMINI_API_KEY") or "").strip()

    def get_gemini_model_name(self) -> str:
        self.load_env()
        return self._gemini_model_id

    def get_gemini_model(self) -> Any:
        """설정된 경우 `google.genai.Client`, 없으면 `None`."""
        self.load_env()
        return self._gemini_client

    def is_gemini_ready(self) -> bool:
        self.load_env()
        return self._gemini_client is not None


def get_keymaker(env_path: Path | None = None) -> Keymaker:
    """애플리케이션 전역에서 사용할 Keymaker 싱글톤."""
    return Keymaker.instance(env_path=env_path)
