from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_explainability():
    return {"message": "Explainability service"}
