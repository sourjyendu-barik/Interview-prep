from fastapi import Cookie, HTTPException, status
from bson import ObjectId

from app.db import users_collection
from app.utils.verify_jwt import verify_jwt
from app.models import UserOut


async def get_current_user(prep_token: str | None = Cookie(default=None)) -> UserOut:
    """
    FastAPI dependency — reads the httpOnly cookie `prep_token`,
    verifies the JWT, fetches the user from DB and returns UserOut.

    Usage on any protected route:
        @router.get("/protected")
        async def protected(user: UserOut = Depends(get_current_user)):
            ...
    """
    if not prep_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated — cookie missing",
        )

    try:
        payload = verify_jwt(prep_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )

    user_id: str = payload.get("sub", "")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user_doc is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return UserOut(
        id=str(user_doc["_id"]),
        name=user_doc.get("name", ""),
        email=user_doc.get("email", ""),
        profilePic=user_doc.get("profilePic", ""),
        totalAvlec=user_doc.get("totalAvlec", 0),
    )
