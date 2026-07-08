from pydantic import BaseModel, Field


class GilfoyleSysSchema(BaseModel):

    id: int = Field(0, description="Piper ID")
    name: str = Field("Gilfoyle Sys", description="Character name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 4,
                "name": "Gilfoyle Sys",
            }
        }
    }
