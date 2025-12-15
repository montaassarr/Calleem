from fastapi import APIRouter

router = APIRouter(prefix="/ai", tags=["AI Chat"])

@router.get("/")
async def placeholder():
    return {"message": "AI Chat disabled"}
