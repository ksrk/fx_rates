from fastapi import FastAPI
from app.api.v1.routes_rates import router as rates_router


app = FastAPI(title="Fx Rate Calculator", version="1.1.0")

app.include_router(rates_router, prefix="/v1")

@app.get("/")
async def root():
    return {"service": "Fx Rate Calculator", "version": "1.1.0"}
