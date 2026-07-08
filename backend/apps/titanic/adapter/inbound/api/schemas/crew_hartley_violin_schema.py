from pydantic import BaseModel, Field


class HartleyViolinSchema(BaseModel):

    id: int = Field(0, description="Crew ID")
    name: str = Field("월리스 하틀리", description="Violinist's name")
    # 침몰 당시 바이올린을 연주하며 승객들을 달랜 승무원 밴드 리더

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 3,
                "name": "Wallace Hartley",
            }
        }
    }
