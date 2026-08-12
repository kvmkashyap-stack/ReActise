from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="User's full name.",
    )
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        description="User password.",
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        description="User password.",
    )


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    token: str = Field(
        ...,
        description="The 6-digit OTP code sent to user's email.",
    )
    type: str = Field(
        default="signup",
        description="The OTP verification type (e.g. signup, recovery, email).",
    )


class ResendOTPRequest(BaseModel):
    email: EmailStr
    type: str = Field(
        default="signup",
        description="The resend verification type (signup, email_change, etc.).",
    )



class AuthResponse(BaseModel):
    user_id: str = Field(..., description="User ID.")
    email: EmailStr = Field(..., description="User email address.")
    access_token: str = Field(..., description="JWT access token.")
    refresh_token: Optional[str] = Field(
        default=None,
        description="JWT refresh token.",
    )
    token_type: str = Field(
        default="bearer",
        description="Token type.",
    )


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token.")
    token_type: str = Field(default="bearer", description="Token type.")


class UserResponse(BaseModel):
    id: str = Field(..., description="User ID.")
    name: Optional[str] = Field(None, description="User name.")
    email: EmailStr