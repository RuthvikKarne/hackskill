from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_forecasts():
    return {"message": "Forecasting service"}
