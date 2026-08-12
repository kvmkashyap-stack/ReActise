from fastapi import APIRouter

from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    VerifyOTPRequest,
    ResendOTPRequest,
)

from app.services.auth_service import (
    signup_user,
    login_user,
    verify_user_otp,
    resend_user_otp,
    logout_user,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)



@router.post("/signup")
def signup(
    request: SignupRequest
):

    return signup_user(request)



@router.post("/login")
def login(
    request: LoginRequest
):

    return login_user(request)



@router.post("/verify-otp")
def verify_otp(
    request: VerifyOTPRequest
):

    return verify_user_otp(request)



@router.post("/resend-otp")
def resend_otp(
    request: ResendOTPRequest
):

    return resend_user_otp(request)



@router.post("/logout")
def logout():

    return logout_user()