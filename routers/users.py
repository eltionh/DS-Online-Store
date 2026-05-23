import sqlite3
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from auth.security import get_api_key
from database import get_db_connection
from models.user import LoginRequest, LoginResponse, User, UserAdminCreate, UserCreate, UserUpdate


router = APIRouter()


@router.post("/auth/register", response_model=LoginResponse)
def register_user(user: UserCreate):
    with get_db_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, 'user')",
                (user.username, user.password),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Username already exists")
    return LoginResponse(username=user.username, role="user")


@router.post("/auth/login", response_model=LoginResponse)
def login_user(login: LoginRequest):
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT username, role FROM users WHERE username = ? AND password = ?",
            (login.username, login.password),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return LoginResponse(username=row["username"], role=row["role"])


@router.get("/users/", response_model=List[User])
def get_users(_: str = Depends(get_api_key)):
    with get_db_connection() as conn:
        rows = conn.execute("SELECT id, username, role FROM users ORDER BY id").fetchall()
    return [dict(row) for row in rows]


@router.post("/users/", response_model=User)
def create_user(user: UserAdminCreate, _: str = Depends(get_api_key)):
    with get_db_connection() as conn:
        try:
            cursor = conn.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (user.username, user.password, user.role),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Username already exists")
    return User(id=cursor.lastrowid, username=user.username, role=user.role)


@router.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: UserUpdate, _: str = Depends(get_api_key)):
    with get_db_connection() as conn:
        existing = conn.execute("SELECT id, role FROM users WHERE id = ?", (user_id,)).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="User not found")

        if existing["role"] == "admin" and user.role != "admin":
            admin_count = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'").fetchone()[0]
            if admin_count <= 1:
                raise HTTPException(status_code=400, detail="Cannot remove the last admin account")

        try:
            if user.password:
                conn.execute(
                    "UPDATE users SET username = ?, password = ?, role = ? WHERE id = ?",
                    (user.username, user.password, user.role, user_id),
                )
            else:
                conn.execute(
                    "UPDATE users SET username = ?, role = ? WHERE id = ?",
                    (user.username, user.role, user_id),
                )
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Username already exists")
    return User(id=user_id, username=user.username, role=user.role)


@router.delete("/users/{user_id}")
def delete_user(user_id: int, _: str = Depends(get_api_key)):
    with get_db_connection() as conn:
        existing = conn.execute("SELECT id, role FROM users WHERE id = ?", (user_id,)).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="User not found")

        if existing["role"] == "admin":
            admin_count = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'").fetchone()[0]
            if admin_count <= 1:
                raise HTTPException(status_code=400, detail="Cannot delete the last admin account")

        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    return {"detail": "User deleted"}
