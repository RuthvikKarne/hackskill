from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_optimizations():
    return {"message": "Optimization service"}
