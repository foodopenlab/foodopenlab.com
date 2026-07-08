from pydantic import BaseModel, Field


class LoweBoatSchema(BaseModel):

    id: int = Field(0, description="Crew ID")
    name: str = Field("해롤드 로우", description="Officer's name")
    # 구명정을 운용하며 여러 명을 구한 다섯 번째 항해사

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 4,
                "name": "Harold Lowe",
            }
        }
    }
