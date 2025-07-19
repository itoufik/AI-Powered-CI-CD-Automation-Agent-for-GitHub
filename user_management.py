from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import List
import uvicorn

app = FastAPI(title="Simple User Management System")

# In-memory storage (replace with a database in production)
users = []

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security for basic auth
security = HTTPBasic()

# User model
class User(BaseModel):
    username: str
    password: str  # This will be hashed

class UserInDB(User):
    hashed_password: str

# Helper to hash password
def hash_password(password: str):
    return pwd_context.hash(password)

# Helper to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Helper to get user by username
def get_user(username: str):
    for user in users:
        if user["username"] == username:
            return user
    return None

# Register a new user
@app.post("/users/", response_model=User)
def create_user(user: User):
    if get_user(user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = hash_password(user.password)
    user_dict = {"username": user.username, "hashed_password": hashed}
    users.append(user_dict)
    return {"username": user.username, "password": "hashed for security"}

# Login endpoint (using basic auth)
@app.post("/login/")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    user = get_user(credentials.username)
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": f"Welcome, {credentials.username}!"}

# Get all users (for demo purposes, no auth required here)
@app.get("/users/", response_model=List[User])
def read_users():
    return [{"username": u["username"], "password": "hidden"} for u in users]

# Get a specific user by username
@app.get("/users/{username}")
def read_user(username: str):
    user = get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": username, "password": "hidden"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
