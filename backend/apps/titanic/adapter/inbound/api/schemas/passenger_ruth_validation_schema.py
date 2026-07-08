from pydantic import BaseModel, Field


class RuthValidationSchema(BaseModel):

    id: int = Field(0, description="Passenger ID")
    name: str = Field("루쓰 드윗 부카터", description="Passenger's name")
    # 로즈의 어머니. 1등급 승객

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 12,
                "name": "Ruth DeWitt Bukater",
            }
        }
    }
