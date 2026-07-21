"""공유 커널 ORM — 두 Bounded Context(mfds_user·mfds_admin)가 공유하는 테이블.

`users` 폴리모픽 identity base와 BC 경계를 넘어 조회되는 테이블을 여기에 둔다.
apps 는 이 패키지를 import 하고(apps→core, 허용), apps 간 직접 참조(spoke↔spoke)는 금지된다.
"""

from matrix.orm.user_orm import UserORM
from matrix.orm.expert_user_orm import ExpertUserORM
from matrix.orm.agent_message_orm import AgentMessageORM
from matrix.orm.expert_whitelist_orm import ExpertWhitelistORM
from matrix.orm.search_log_orm import SearchLogORM

__all__ = [
    "UserORM",
    "ExpertUserORM",
    "AgentMessageORM",
    "ExpertWhitelistORM",
    "SearchLogORM",
]
