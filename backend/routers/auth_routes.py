"""
auth_routes.py
JWT signup / login / profile endpoints.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional

from models.user_schemas import UserCreate, UserLogin, UserUpdate, UserResponse, TokenResponse
from services.auth_service import hash_password, verify_password, create_access_token, decode_token
from services.db_service import db_service

router = APIRouter(prefix="/auth", tags=["auth"])


# ── dependency ──────────────────────────────────────────────────────────────

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Extract and validate JWT from the Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get("sub")
    user = await db_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ── endpoints ────────────────────────────────────────────────────────────────

@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(body: UserCreate):
    """Register a new user."""
    existing = await db_service.get_user_by_email(body.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed = hash_password(body.password)
    now = datetime.now(timezone.utc).isoformat()
    user_doc = {
        "name": body.name,
        "email": body.email,
        "password": hashed,
        "created_at": now,
    }
    inserted_id = await db_service.create_user(user_doc)
    if not inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create user")

    token = create_access_token(user_id=inserted_id, email=body.email)
    return TokenResponse(
        access_token=token,
        user=UserResponse(id=inserted_id, name=body.name, email=body.email, created_at=now),
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin):
    """Authenticate and return a JWT."""
    user = await db_service.get_user_by_email(body.email)
    if not user or not verify_password(body.password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = user["_id"]
    token = create_access_token(user_id=user_id, email=user["email"])
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            name=user["name"],
            email=user["email"],
            created_at=user.get("created_at", ""),
        ),
    )


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return UserResponse(
        id=current_user["_id"],
        name=current_user["name"],
        email=current_user["email"],
        created_at=current_user.get("created_at", ""),
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(body: UserUpdate, current_user: dict = Depends(get_current_user)):
    """Update allowed profile fields."""
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    user_id = current_user["_id"]
    ok = await db_service.update_user(user_id, updates)
    if not ok:
        raise HTTPException(status_code=500, detail="Profile update failed")

    updated = await db_service.get_user_by_id(user_id)
    return UserResponse(
        id=updated["_id"],
        name=updated["name"],
        email=updated["email"],
        created_at=updated.get("created_at", ""),
    )


@router.get("/my-courses")
async def my_courses(current_user: dict = Depends(get_current_user)):
    """Return courses linked to the authenticated user."""
    user_id = current_user["_id"]
    courses = await db_service.get_user_courses(user_id)
    return {"success": True, "courses": courses}
