import os
from passlib.context import CryptContext

# Force passlib to use pure-python bcrypt backend (stable on Ubuntu/WSL)
os.environ["PASSLIB_USE_CEXT_BCRYPT"] = "0"

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)
