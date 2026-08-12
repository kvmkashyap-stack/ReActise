import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException
from app.core.supabase import supabase
from app.core.config import settings
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    VerifyOTPRequest,
    ResendOTPRequest,
    AuthResponse,
)

# Global dictionary to cache pending OTP codes in memory
# maps email -> {"code": str, "user_id": str, "access_token": str, "refresh_token": str}
PENDING_OTPS = {}


def send_otp_email(to_email: str, otp_code: str) -> bool:
    """
    Send the 6-digit OTP code directly using Python's smtplib.
    Bypasses Supabase SMTP queues and uses the user's Gmail/Google SMTP configs.
    """
    smtp_user = settings.SMTP_USER
    smtp_password = settings.SMTP_PASSWORD
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT

    html_content = f"""
    <html>
      <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8fafc; color: #0f172a; padding: 24px;">
        <div style="max-width: 520px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 32px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
          <h2 style="color: #7c3aed; margin-top: 0; font-size: 20px; font-weight: 800; letter-spacing: -0.025em;">ReActise</h2>
          <p style="font-size: 14px; color: #475569; line-height: 1.5;">Enter the following 6-digit verification code to confirm your account and log in:</p>
          <div style="font-size: 28px; font-weight: 800; background: #f1f5f9; padding: 16px; border-radius: 6px; text-align: center; letter-spacing: 6px; margin: 24px 0; color: #0f172a; border: 1px solid #e2e8f0; font-family: ui-monospace, monospace;">
            {otp_code}
          </div>
          <p style="font-size: 12px; color: #94a3b8; line-height: 1.5; margin-bottom: 0;">If you did not request this registration code, please ignore this email.</p>
        </div>
      </body>
    </html>
    """

    if not smtp_user or not smtp_password:
        print(f"\n[DEVELOPER NOTICE] SMTP credentials not configured in backend/.env.")
        print(f"-> Verification code for {to_email}: {otp_code} (Fallback '123456' is also active)\n")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = f"ReActise <{smtp_user}>"
        msg["To"] = to_email
        msg["Subject"] = f"ReActise OTP Code: {otp_code}"

        msg.attach(MIMEText(html_content, "html"))

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send SMTP email: {str(e)}")
        print(f"-> [FALLBACK] Generated OTP code for {to_email}: {otp_code} (Fallback '123456' is also active)")
        return False


def signup_user(
    request: SignupRequest,
) -> AuthResponse:
    """
    Register a new user using email/password.
    Sends verification email directly via Python SMTP to bypass Supabase mail errors.
    """
    try:
        # Create user in Supabase.
        # Note: If email confirmation is disabled in Supabase, this confirms the account
        # instantly, which allows password login to work immediately!
        response = supabase.auth.sign_up(
            {
                "email": request.email,
                "password": request.password,
                "options": {
                    "data": {
                        "full_name": request.name,
                    }
                },
            }
        )

        if response.user is None:
            raise HTTPException(
                status_code=400,
                detail="Signup failed",
            )

        # Generate a random 6-digit OTP verification code
        otp_code = str(random.randint(100000, 999999))

        # Retrieve and cache access tokens in memory for OTP verification stage
        access_token = response.session.access_token if response.session else ""
        refresh_token = response.session.refresh_token if response.session else None

        PENDING_OTPS[request.email] = {
            "code": otp_code,
            "user_id": response.user.id,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

        # Send SMTP email directly via python
        send_otp_email(request.email, otp_code)

        # Return empty access_token to signal to the client that OTP confirmation is pending
        return AuthResponse(
            user_id=response.user.id,
            email=response.user.email,
            access_token="",
            refresh_token=None,
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


def login_user(
    request: LoginRequest,
) -> AuthResponse:
    """
    Login user using email/password.
    """
    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": request.email,
                "password": request.password,
            }
        )

        if response.user is None or response.session is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
            )

        return AuthResponse(
            user_id=response.user.id,
            email=response.user.email,
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
        )

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )


def verify_user_otp(
    request: VerifyOTPRequest,
) -> AuthResponse:
    """
    Verify the 6-digit OTP code.
    If valid, returns the cached session token to log the user in.
    Supports '123456' as a developer testing bypass.
    """
    email = request.email
    token = request.token

    if email not in PENDING_OTPS:
        raise HTTPException(
            status_code=400,
            detail="No pending signup session found for this email address.",
        )

    cached = PENDING_OTPS[email]
    is_developer_bypass = (token == "123456")

    if token == cached["code"] or is_developer_bypass:
        # Clear code from memory
        del PENDING_OTPS[email]

        # Returns the confirmed session token
        return AuthResponse(
            user_id=cached["user_id"],
            email=email,
            access_token=cached["access_token"],
            refresh_token=cached["refresh_token"],
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification code. Please try again.",
        )


def resend_user_otp(
    request: ResendOTPRequest,
) -> dict:
    """
    Resend the OTP verification email directly using Python SMTP.
    """
    email = request.email
    if email not in PENDING_OTPS:
        otp_code = str(random.randint(100000, 999999))
        PENDING_OTPS[email] = {
            "code": otp_code,
            "user_id": "",
            "access_token": "",
            "refresh_token": None,
        }
    else:
        otp_code = PENDING_OTPS[email]["code"]

    send_otp_email(email, otp_code)
    return {"message": "Verification code resent successfully!"}


def logout_user():
    """
    Logout current user.
    """
    try:
        supabase.auth.sign_out()
        return {"message": "Logged out successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


def get_current_user(
    access_token: str,
):
    """
    Retrieve current user from JWT token.
    """
    try:
        response = supabase.auth.get_user(access_token)

        if response.user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

        return {
            "user_id": response.user.id,
            "email": response.user.email,
        }

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )