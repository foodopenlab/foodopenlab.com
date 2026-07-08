from __future__ import annotations

import logging

from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession
from titanic.adapter.outbound.mappers.crew_james_director_mapper import (
    upload_entities_to_persistence_rows,
)
from titanic.adapter.outbound.orm.passenger_jack_trainer_orm import JackTrainerOrm
from titanic.adapter.outbound.orm.titanic_booking_orm import TitanicBookingOrm
from titanic.app.dtos.crew_james_director_dto import JamesDirectorQuery, JamesDirectorResponse
from titanic.domain.entities.passenger_jack_trainer_entity import JackPassenger
from titanic.domain.entities.passenger_rose_model_entity import RoseBooking

logger = logging.getLogger("titanic.upload")

_BATCH_SIZE = 200


async def _upsert_batch(session, table, rows: list[dict], pk: str) -> None:
    if not rows:
        return
    stmt = insert(table).values(rows)
    excluded = stmt.excluded
    update_cols = {
        column.name: getattr(excluded, column.name)
        for column in table.columns
        if column.name != pk
    }
    stmt = stmt.on_conflict_do_update(index_elements=[pk], set_=update_cols)
    await session.execute(stmt)


class JamesDirectorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def receive_uploaded_records(
        self,
        passengers: list[JackPassenger],
        bookings: list[RoseBooking],
    ) -> int:
        logger.info("[제임스 레포지터리] JackPassenger 상위 5개:")
        for passenger in passengers[:5]:
            logger.info("%s", passenger)

        logger.info("[제임스 레포지터리] RoseBooking 상위 5개:")
        for booking in bookings[:5]:
            logger.info("%s", booking)

        persons, booking_rows = upload_entities_to_persistence_rows(passengers, bookings)
        if not persons:
            return 0

        person_table = JackTrainerOrm.__table__
        booking_table = TitanicBookingOrm.__table__

        try:
            for offset in range(0, len(persons), _BATCH_SIZE):
                person_batch = persons[offset : offset + _BATCH_SIZE]
                booking_batch = booking_rows[offset : offset + _BATCH_SIZE]
                await _upsert_batch(self._session, person_table, person_batch, "passenger_id")
                await _upsert_batch(self._session, booking_table, booking_batch, "passenger_id")
            await self._session.commit()
        except ProgrammingError as exc:
            logger.exception("titanic 테이블 스키마 오류")
            raise HTTPException(
                status_code=503,
                detail="DB 스키마가 준비되지 않았습니다. alembic upgrade head 후 서버를 재시작하세요.",
            ) from exc
        except OperationalError as exc:
            logger.exception("titanic DB 연결 실패")
            raise HTTPException(
                status_code=503,
                detail="DB에 연결할 수 없습니다. DATABASE_URL과 Neon 상태를 확인하세요.",
            ) from exc
        except IntegrityError as exc:
            logger.exception("titanic DB 무결성 오류")
            raise HTTPException(
                status_code=409,
                detail="승객·예약 데이터 저장 중 충돌이 발생했습니다.",
            ) from exc

        saved = len(persons)
        logger.info("[제임스 레포지터리] Neon 저장 완료 saved=%s", saved)
        return saved

    async def introduce_myself(self, query: JamesDirectorQuery) -> JamesDirectorResponse:
        logger.info("[JamesDirectorRepository] introduce_myself 진입 | request_data=%s", query)

        return JamesDirectorResponse(
            id=query.id * 10000,
            name=query.name + "가 레포지토리에 다녀옴",
        )
