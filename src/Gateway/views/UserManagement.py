from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/user",
)


@router.post("/")
async def handle_root():
    return "Hello to the UserManagement World"
