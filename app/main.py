from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import engine, SessionLocal
from app import models, schemas
from app.security import hash_password, verify_password
from app.auth import create_access_token, get_current_user, require_admin

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Attendance System API")


# ---------- DATABASE DEPENDENCY ----------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- ROOT ----------

@app.get("/")
def root():
    return {"status": "Project 2 backend running"}


# ---------- USER ROUTES ----------

@app.post("/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)

    db_user = models.User(
        name=user.name,
        email=user.email,
        role=user.role,
        password_hash=hashed_pw
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ---------- AUTH ----------

@app.post("/auth/login")
def login(user: schemas.LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        data={"sub": str(db_user.id), "role": db_user.role}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ---------- EMPLOYEE ROUTES ----------

@app.post("/attendance/check-in", response_model=schemas.AttendanceResponse)
def check_in(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    record = models.Attendance(user_id=current_user["user_id"])
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.put("/attendance/check-out/{attendance_id}", response_model=schemas.AttendanceResponse)
def check_out(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    record = db.query(models.Attendance).filter(
        models.Attendance.id == attendance_id,
        models.Attendance.user_id == current_user["user_id"]
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    record.check_out_time = datetime.utcnow()
    record.status = "checked_out"

    db.commit()
    db.refresh(record)
    return record


# ---------- ADMIN ROUTES ----------

@app.get("/admin/users", response_model=list[schemas.UserResponse])
def list_all_users(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    return db.query(models.User).all()


@app.get("/admin/attendance", response_model=list[schemas.AttendanceResponse])
def list_all_attendance(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    return db.query(models.Attendance).all()
