import os
import httpx
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from dotenv import load_dotenv

from app.db import users_collection
from app.models import User, UserOut, LoginRequest
from app.utils.create_jwt import create_jwt
from app.utils.setSecureCookie import set_secure_cookie
from app.dependencies import get_current_user

load_dotenv()

# ── Public routes  (no auth required) ────────────────────────────────────────
public_router = APIRouter(prefix="/auth", tags=["Auth"])

# ── Private routes (valid cookie required on every route) ────────────────────
private_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    dependencies=[Depends(get_current_user)],
)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "postmessage"  # used when client sends auth-code via useGoogleLogin


# ─────────────────────────────────────────────
#  POST /auth/login  ← PUBLIC
#  Body: { "code": "<google auth code>" }
# ─────────────────────────────────────────────
@public_router.post("/login", response_model=UserOut)
async def google_login(response: Response, body: LoginRequest):
    code = body.code
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is required")

    # ── 1. Exchange code for Google tokens ──────────────────────────────────
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )

    if token_res.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to exchange code: {token_res.text}",
        )

    tokens = token_res.json()
    access_token: str = tokens.get("access_token", "")

    # ── 2. Fetch Google user profile ─────────────────────────────────────────
    async with httpx.AsyncClient() as client:
        user_info_res = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    if user_info_res.status_code != 200:
        raise HTTPException(status_code=401, detail="Failed to fetch user info from Google")

    google_user = user_info_res.json()
    google_id: str = google_user.get("id", "")
    name: str = google_user.get("name", "")
    email: str = google_user.get("email", "")
    picture: str = google_user.get("picture", "")

    # ── 3. Upsert user in MongoDB ────────────────────────────────────────────
    now = datetime.now(timezone.utc)

    existing_user = await users_collection.find_one({"googleId": google_id})

    if existing_user is None:
        # Create new user using the typed User model
        new_user_model = User(
            googleId=google_id,
            name=name,
            email=email,
            profilePic=picture,
        )
        new_user: dict[str, Any] = new_user_model.model_dump()
        result = await users_collection.insert_one(new_user)
        user_id = str(result.inserted_id)
        user_doc: dict[str, Any] = {**new_user, "_id": result.inserted_id}
    else:
        # Update updatedAt timestamp
        await users_collection.update_one(
            {"googleId": google_id},
            {"$set": {"updatedAt": now}},
        )
        user_doc = dict(existing_user)
        user_id = str(user_doc["_id"])

    # ── 4. Create JWT ────────────────────────────────────────────────────────
    jwt_token = create_jwt({"sub": user_id, "email": email})

    # ── 5. Set httpOnly cookie ───────────────────────────────────────────────
    set_secure_cookie(response, jwt_token)

    # ── 6. Return user details ───────────────────────────────────────────────
    return UserOut(
        id=user_id,
        name=user_doc.get("name", name),
        email=user_doc.get("email", email),
        profilePic=user_doc.get("profilePic", picture),
        totalAvlec=user_doc.get("totalAvlec", 0),
    )


# ─────────────────────────────────────────────
#  POST /auth/logout  ← PRIVATE
#  Clears the httpOnly cookie to end session
# ─────────────────────────────────────────────
@private_router.post("/logout")
async def logout(
    response: Response,
    current_user: UserOut = Depends(get_current_user),
):
    """Clear the auth cookie. Requires a valid session (cookie must exist)."""
    response.delete_cookie(
        key="prep_token",
        httponly=True,
        # samesite="none",  # uncomment for deployment with secure=True
        # secure=True,
    )
    return {"message": f"Logged out successfully. Goodbye, {current_user.name}!"}


# ─────────────────────────────────────────────
#  GET /auth/me  ← PRIVATE
#  Called by client on every page refresh.
# ─────────────────────────────────────────────
@private_router.get("/me", response_model=UserOut)
async def get_me(current_user: UserOut = Depends(get_current_user)):
    """Return the currently authenticated user's details."""
    return current_user
