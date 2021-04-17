from pydantic import BaseModel


class DBBaseModel(BaseModel):

    @classmethod
    def from_db_model(cls, model):
        return cls(**model.__dict__)
