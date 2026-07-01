from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_risk_intelligence():
    return {"message": "Risk Intelligence service"}
