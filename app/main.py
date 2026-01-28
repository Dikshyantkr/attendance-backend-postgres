from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import engine, SessionLocal
from app import models, schemas
from app.security import encrypt_text, decrypt_text, hash_password

# create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Attendance System API")

# ---------------- DB DEPENDENCY ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "Project 2 backend running"}

# ---------------- USERS ----------------
@app.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    encrypted_email = encrypt_text(user.email)

    db_user = models.User(
        name=user.name,
        email=encrypted_email,
        role=user.role,
        password_hash=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # decrypt email before sending response
    db_user.email = decrypt_text(db_user.email)
    return db_user


@app.get("/users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    for u in users:
        u.email = decrypt_text(u.email)
    return users

# ---------------- ATTENDANCE ----------------
@app.post("/attendance/check-in", response_model=schemas.AttendanceResponse)
def check_in(attendance: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    record = models.Attendance(
        user_id=attendance.user_id,
        check_in_time=datetime.utcnow(),
        status="checked_in"
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.post("/attendance/check-out/{attendance_id}", response_model=schemas.AttendanceResponse)
def check_out(attendance_id: int, db: Session = Depends(get_db)):
    record = (
        db.query(models.Attendance)
        .filter(models.Attendance.id == attendance_id)
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    record.check_out_time = datetime.utcnow()
    record.status = "checked_out"

    db.commit()
    db.refresh(record)
    return record
