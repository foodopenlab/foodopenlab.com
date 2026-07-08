from pydantic import BaseModel, Field


class RoseModelSchema(BaseModel):

    id: int = Field(0, description="Passenger ID")
    name: str = Field("로즈 드윗 부카터", description="Passenger's name")
    # 1등급 승객. 영화 속 주인공

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 11,
                "name": "Rose DeWitt Bukater",
            }
        }
    }
