from pydantic import BaseModel
from datetime import datetime


# ---------- USER SCHEMAS ----------

class UserCreate(BaseModel):
    name: str
    email: str
    role: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str


# ---------- ATTENDANCE SCHEMAS ----------

class AttendanceCreate(BaseModel):
    user_id: int


class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    check_in_time: datetime
    check_out_time: datetime | None
    status: str

    class Config:
        from_attributes = True
