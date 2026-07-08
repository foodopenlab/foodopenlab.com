from pydantic import BaseModel, Field


class HendricksCeoSchema(BaseModel):

    id: int = Field(0, description="Piper ID")
    name: str = Field("헨드릭스 CEO (Hendricks CEO)", description="Character name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 5,
                "name": "헨드릭스 CEO (Hendricks CEO)",
            }
        }
    }
