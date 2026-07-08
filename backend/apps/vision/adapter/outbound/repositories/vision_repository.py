from __future__ import annotations

import asyncio
import logging
import uuid
from pathlib import Path

from vision.app.dtos.vision_dto import VisionQuery, VisionResponse, VisionUploadQuery, VisionUploadResult
from vision.app.ports.output.vision_port import IVisionPort

logger = logging.getLogger(__name__)

_UPLOAD_DIR = Path(__file__).resolve().parents[5] / "data" / "vision_uploads"


class VisionRepository(IVisionPort):
    async def introduce_myself(self, query: VisionQuery) -> VisionResponse:
        logger.info("[VisionRepository] introduce_myself | request=%s", query)
        return VisionResponse(id=query.id, name=query.name)

    async def save_image(self, query: VisionUploadQuery) -> VisionUploadResult:
        image_id = uuid.uuid4().hex
        extension = Path(query.filename).suffix.lower()
        stored_path = _UPLOAD_DIR / f"{image_id}{extension}"

        def _write() -> None:
            _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            stored_path.write_bytes(query.content)

        await asyncio.to_thread(_write)
        logger.info("[VisionRepository] save_image | id=%s filename=%s size=%d", image_id, query.filename, len(query.content))
        return VisionUploadResult(
            id=image_id,
            filename=query.filename,
            content_type=query.content_type,
            size=len(query.content),
        )
