from fastapi import APIRouter, HTTPException, Query, status
from structlog.stdlib import get_logger
from app.models.schemas import FxResponse
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
