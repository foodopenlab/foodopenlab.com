from pydantic import BaseModel, Field


class DineshDashSchema(BaseModel):

    id: int = Field(0, description="Piper ID")
    name: str = Field("디네시 대시 (Dinesh Dash)", description="Character name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 2,
                "name": "디네시 대시 (Dinesh Dash)",
            }
        }
    }
