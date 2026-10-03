from pydantic import BaseModel


class MerchantRead(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
