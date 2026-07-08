from pydantic import BaseModel, Field


class MollyScalerSchema(BaseModel):

    id: int = Field(0, description="Passenger ID")
    name: str = Field("몰리 브라운", description="Passenger's name")
    # 구명정에 돌아가 추가 승객을 구하려 했던 1등급 승객

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 10,
                "name": "Margaret 'Molly' Brown",
            }
        }
    }
