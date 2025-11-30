from pydantic import BaseModel, Field, ConfigDict

class Base(BaseModel):
    pass

class App(Base):
    id: str = Field(alias="_id")

class AppResp(App):
    id: str # Override
    model_config = ConfigDict(populate_by_name=True)

data = {"id": "123", "_id": "123"}
model = AppResp(**data)
print(f"Model dump (by_alias=True): {model.model_dump(by_alias=True)}")
