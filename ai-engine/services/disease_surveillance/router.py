from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_disease_surveillance():
    return {"message": "Disease Surveillance service"}
