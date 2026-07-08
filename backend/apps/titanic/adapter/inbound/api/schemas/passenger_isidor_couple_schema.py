from pydantic import BaseModel, Field


class IsidorCoupleSchema(BaseModel):

    id: int = Field(0, description="Passenger ID")
    name: str = Field("이시도르 스트라우스", description="Passenger's name")
    # 마시 백화점 공동 창업자. 아내와 함께 침실에서 기다리며 사망한 부부

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 8,
                "name": "Isidor Straus",
            }
        }
    }
