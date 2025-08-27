from pydantic import BaseModel, Field


class FxResponse(BaseModel):
    currency: str = Field(..., alias="currency", description="Currency")
    quantity: float = Field(..., alias="quantity", description="Quantity")