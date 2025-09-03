from fastapi import APIRouter, HTTPException, Query, status
from structlog.stdlib import get_logger
from app.models.schemas import (FxResponse,
                                OverrideFxRateRequest,
                                OverrideFxRateResponse)
from app.services.rate_service import RateService

logger = get_logger()

router = APIRouter(prefix="/rates", tags=["rates"])
service = RateService()

@router.get("/fx-rate", response_model=FxResponse)
async def get_fx_rate(ccy_from: str = Query(..., min_length=3, max_length=3),
                      ccy_to: str = Query(..., min_length=3, max_length=3),
                      quantity:int = Query(..., gt=0) ) -> FxResponse:
    logger.info("Get fx rate", ccy_from=ccy_from, quantity=quantity)
    try:
        return await service.get_rate(ccy_from, ccy_to, quantity)
    except ValueError as e:
        logger.error(f"Error getting fx rate", error=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Exception while getting fx rate", error=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/fx-rate/override", response_model=OverrideFxRateResponse,
             status_code=status.HTTP_200_OK)
async def override_fx_rate(payload: OverrideFxRateRequest):
    pair = f"{payload.ccy_from.upper()}{payload.ccy_to.upper()}"
    try:
        return await service.ccy_override(pair, payload.fx_rate)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/fx-rate/clear", response_model=OverrideFxRateResponse,
               status_code=status.HTTP_200_OK)
async def clear_fx_rate(
    ccy_pair: str = Query(..., min_length=6, max_length=7),
):
    pair = ccy_pair.replace("/", "").upper()
    try:
        return await service.clear_fx_rate_override(pair)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))