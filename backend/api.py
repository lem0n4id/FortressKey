from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from password_manager import PasswordManager
import uvicorn

app = FastAPI()

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate PasswordManager
password_manager = PasswordManager()

# Define models for the requests
class UserRegistration(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class PasswordEntry(BaseModel):
    website: str
    username: str
    password: str

class PasswordUpdate(BaseModel):
    website: str
    username: str
    new_password: str

# Route to register a new user
@app.post("/register")
def register(user: UserRegistration):
    if not password_manager.register_user(user.username, user.password):
        raise HTTPException(status_code=400, detail="User already exists")
    return {"message": "User registered successfully"}

# Route for user login
@app.post("/login")
def login(user: UserLogin):
    if not password_manager.login_user(user.username, user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"success": True, "message": "Login successful"}

# Route to add a password entry for the logged-in user
@app.post("/add-password")
def add_password(password_entry: PasswordEntry, user: UserLogin):
    if not password_manager.login_user(user.username, user.password):
        raise HTTPException(status_code=403, detail="Unauthorized")

    success = password_manager.add_password(password_entry.website, password_entry.username, password_entry.password)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add password")
    return {"success": True, "message": "Password added successfully"}

# Route to get all password entries for the logged-in user
@app.get("/get-passwords")
def get_passwords(user: UserLogin):
    if not password_manager.login_user(user.username, user.password):
        raise HTTPException(status_code=403, detail="Unauthorized")

    passwords = password_manager.get_all_passwords()
    if passwords is None:
        raise HTTPException(status_code=404, detail="No passwords found")
    return {"passwords": passwords}

# Route to update an existing password
@app.put("/update-password")
def update_password(password_update: PasswordUpdate, user: UserLogin):
    if not password_manager.login_user(user.username, user.password):
        raise HTTPException(status_code=403, detail="Unauthorized")

    success = password_manager.update_password(password_update.website, password_update.username, password_update.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update password")
    return {"success": True, "message": "Password updated successfully"}

if __name__ == "__main__":
	uvicorn.run("api:app", port=5000, reload=True)