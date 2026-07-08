from pydantic import BaseModel, Field


class AndrewsArchitectSchema(BaseModel):

    id: int = Field(0, description="Crew ID")
    name: str = Field("토마스 앤드류스", description="Architect's name")
    # 타이타닉 설계자. 침몰 시 선내를 돌아다니며 승객들을 구명정으로 안내한 것으로 알려짐

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 2,
                "name": "Thomas Andrews",
            }
        }
    }
