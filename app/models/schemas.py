from pydantic import BaseModel, Field


class FxResponse(BaseModel):
    currency: str = Field(..., alias="currency", description="Currency")
    quantity: float = Field(..., alias="quantity", description="Quantity")


class OverrideFxRateResponse(BaseModel):
    code: int = Field(..., alias="code", description="Status Code")
    status: str = Field(..., alias="status", description="Status")


class OverrideFxRateRequest(BaseModel):
    ccy_from: str = Field(..., min_length=3, max_length=3)
    ccy_to: str = Field(..., min_length=3, max_length=3)
    fx_rate: float = Field(..., gt=0)