from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class Base(BaseModel):
    pass

class App(Base):
    id: str = Field(alias="_id")

class AppResp(App):
    model_config = ConfigDict(populate_by_name=True)

data = {"id": "123", "_id": "123"}
model = AppResp(**data)
print(f"Model dump (default): {model.model_dump()}")
print(f"Model dump (by_alias=True): {model.model_dump(by_alias=True)}")
print(f"Model dump (by_alias=False): {model.model_dump(by_alias=False)}")
print(f"Model json: {model.model_dump_json()}")
