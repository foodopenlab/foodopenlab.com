from pydantic import BaseModel, Field


class BighettiHrSchema(BaseModel):

    id: int = Field(0, description="Piper ID")
    name: str = Field("빅헤티 HR (Bighetti HR)", description="Character name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "빅헤티 HR (Bighetti HR)",
            }
        }
    }
