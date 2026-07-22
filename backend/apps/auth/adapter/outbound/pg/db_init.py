"""auth 신원 = 공유 유저 테이블(core `ExpertUserORM`, `expert_users`).

별도 auth 테이블을 만들지 않는다. 테이블 생성은 mfds_user의 `create_user_tables`가
공유 DB에 이미 수행한다. 여기서는 모델을 import해 SQLAlchemy 매핑에 등록만 한다.
"""

from __future__ import annotations

import logging

# import만으로 ExpertUserORM이 metadata에 등록된다(auth의 쿼리·standalone auth_main용).
from matrix.orm.expert_user_orm import ExpertUserORM  # noqa: F401

logger = logging.getLogger(__name__)


async def create_auth_tables() -> None:
    logger.info("auth: 공유 유저 테이블(expert_users) 사용 — 별도 테이블 생성 없음")
