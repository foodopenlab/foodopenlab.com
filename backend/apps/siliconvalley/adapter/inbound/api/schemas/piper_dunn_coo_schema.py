from pydantic import BaseModel, Field


class DunnCooSchema(BaseModel):

    id: int = Field(0, description="Piper ID")
    name: str = Field("던 COO (Dunn COO)", description="Character name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 3,
                "name": "던 COO (Dunn COO)",
            }
        }
    }
