from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.services.gmail_oauth_service import get_auth_url, handle_callback

router = APIRouter(prefix="/auth/google", tags=["Google OAuth"])

@router.get("/login")
def login():
    return RedirectResponse(get_auth_url())

@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    return await handle_callback(code)
